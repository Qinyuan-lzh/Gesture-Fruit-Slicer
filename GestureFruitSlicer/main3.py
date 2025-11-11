import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time

# 1. 初始化摄像头和手部检测器
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# -----------------------------------------------------------
# -- 黑边裁切 解决方案 (960x576) --
# -----------------------------------------------------------
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"摄像头实际分辨率: {width} x {height} (带黑边)")

crop_x_start = 160
crop_x_end = 1120
new_width = 960
crop_y_start = 72
crop_y_end = 648
new_height = 576

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", new_width, new_height)
print(f"窗口已强制设置为: {new_width} x {new_height} (无黑边)")
# -----------------------------------------------------------

detector = HandDetector(detectionCon=0.8, maxHands=1)


# 2. ------------------- 中文路径读取函数 -------------------
def cv_imread_chinese(file_path, flags=cv2.IMREAD_UNCHANGED):
    try:
        img_data = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(img_data, flags)
        if img is None:
            raise IOError(f"cv2.imdecode failed for {file_path}")
        return img
    except Exception as e:
        print(f"Error reading chinese path image {file_path}: {e}")
        return None


# 3. ------------------- Fruit 类 -------------------
class Fruit:
    def __init__(self, img, w, h, fruit_type='fruit', image_name="unknown"):
        self.img = img
        self.w = w
        self.h = h
        self.radius = w // 2
        self.fruit_type = fruit_type
        self.image_name = image_name
        self.x = random.randint(100, new_width - 100)
        self.y = new_height
        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-30, -15)
        self.gravity = 0.8

    def update(self, is_frozen=False):
        if is_frozen:
            self.vy += self.gravity * 0.1
            self.x += self.vx * 0.1
            self.y += self.vy * 0.1
        else:
            self.vy += self.gravity
            self.x += self.vx
            self.y += self.vy

        if self.y > new_height + self.h:
            return True
        return False

    def draw(self, imgMain):
        try:
            imgMain = cvzone.overlayPNG(imgMain, self.img,
                                        (int(self.x - self.w // 2),
                                         int(self.y - self.h // 2)))
        except:
            pass
        return imgMain


# 4. ------------------- 加载所有素材 -------------------
fruitImages = []
fruitFiles = ["orange.png", "apple.png", "pineapple.png", "watermelon.png", "banana.png",
              "Lemon.png", "durian.png", "Mango.png", "strawberry.png"]
target_size = (100, 100)

for file in fruitFiles:
    try:
        img = cv_imread_chinese(file)
        if img is None: raise ValueError("图片加载后仍为 None")
        img = cv2.resize(img, target_size)
        h, w, _ = img.shape
        fruitImages.append((img, w, h, file))
        print(f"成功加载: {file}")
    except Exception as e:
        print(f"错误: 无法加载 '{file}'。 {e}")

try:
    imgBomb = cv_imread_chinese("bomb.png")
    imgBomb = cv2.resize(imgBomb, target_size)
    hBomb, wBomb, _ = imgBomb.shape
    print("成功加载: bomb.png")
except:
    imgBomb = np.zeros((100, 100, 4), dtype=np.uint8);
    cv2.circle(imgBomb, (50, 50), 40, (50, 50, 50, 255), cv2.FILLED);
    hBomb, wBomb = 100, 100
if not fruitImages: print("错误：没有任何水果图片加载成功！程序退出。"); exit()

# 5. ------------------- 游戏主变量 -------------------
fruitList = []
trailPoints = []
trailLength = 15
spawnChanceFruit = 0.03
spawnChanceBomb = 0.005
score = 0
freezeTime = 0.0
freezeDuration = 3.0

# --- ⬇️⬇️⬇️ 新增：游戏状态变量 ⬇️⬇️⬇️ ---
gameState = "MENU"  # "MENU", "RUNNING", "GAME_OVER"
gameMode = None  # "INFINITE" or "COUNTDOWN"
countdownDuration = 60.0  # 倒计时模式时长
countdownStartTime = 0.0
# --- ⬆️⬆️⬆️ --------------------------- ---

# 6. ------------------- 游戏主循环 (已重构) -------------------
while True:
    success, img = cap.read()
    if not success:
        break

    # --- 裁切黑边 (始终执行) ---
    img = img[crop_y_start:crop_y_end, crop_x_start:crop_x_end]

    # --- 翻转 (始终执行) ---
    img = cv2.flip(img, 1)

    # --- 手部检测 (始终执行) ---
    hands, img = detector.findHands(img, flipType=False)

    # --- 检查冰冻状态 (在 RUNNING 状态下才有用) ---
    is_frozen_now = time.time() < freezeTime

    # ==============================================================
    # ------------------- 状态一：菜单 (MENU) -------------------
    # ==============================================================
    if gameState == "MENU":
        # 绘制菜单提示
        cvzone.putTextRect(img, "Show FIST for Infinite", [150, 200],
                           scale=3, thickness=3, offset=10)
        cvzone.putTextRect(img, "Show PALM for Countdown", [150, 350],
                           scale=3, thickness=3, offset=10,
                           colorR=(0, 200, 0))  # 绿色

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)

            # 1. 检测到拳头
            if fingers == [0, 0, 0, 0, 0]:
                print("选择了：无限模式")
                gameState = "RUNNING"
                gameMode = "INFINITE"
                # 重置游戏变量
                fruitList = [];
                trailPoints = [];
                score = 0;
                freezeTime = 0.0

            # 2. 检测到手掌
            elif fingers == [1, 1, 1, 1, 1]:
                print("选择了：倒计时模式")
                gameState = "RUNNING"
                gameMode = "COUNTDOWN"
                # 重置游戏变量
                fruitList = [];
                trailPoints = [];
                score = 0;
                freezeTime = 0.0
                countdownStartTime = time.time()  # 开始计时

    # ===============================================================
    # ------------------- 状态二：游戏运行中 (RUNNING) -------------------
    # ===============================================================
    elif gameState == "RUNNING":
        if hands:
            lmList = hands[0]['lmList']
            pointIndex = lmList[8][0:2]
            pointIndex = tuple(pointIndex)
            trailPoints.append(pointIndex)
            if len(trailPoints) > trailLength:
                trailPoints.pop(0)

            # C1. 碰撞检测
            for i in range(len(fruitList) - 1, -1, -1):
                fruit = fruitList[i]
                is_sliced = False
                for pt in trailPoints:
                    dist = math.hypot(pt[0] - fruit.x, pt[1] - fruit.y)

                    if dist < fruit.radius:
                        if fruit.fruit_type == 'fruit':
                            fruitList.pop(i)
                            score += 1
                            is_sliced = True
                            if fruit.image_name == "Lemon.png":
                                freezeTime = time.time() + freezeDuration
                            break
                        elif fruit.fruit_type == 'bomb':
                            # --- ⬇️⬇️⬇️ 修改：切到炸弹，游戏结束 ⬇️⬇️⬇️ ---
                            gameState = "GAME_OVER"
                            is_sliced = True
                            break
                if is_sliced:
                    if gameState == "GAME_OVER": break  # 如果游戏结束，立刻跳出外层循环
                    continue
        else:
            trailPoints = []

        # C2. 随机生成水果 (只在非冰冻时)
        if not is_frozen_now:
            if random.random() < spawnChanceFruit:
                img_f, w_f, h_f, file_name = random.choice(fruitImages)
                fruitList.append(Fruit(img_f, w_f, h_f, 'fruit', file_name))
            if random.random() < spawnChanceBomb:
                fruitList.append(Fruit(imgBomb, wBomb, hBomb, 'bomb', "bomb.png"))

        # C4. 更新和绘制水果
        for i in range(len(fruitList) - 1, -1, -1):
            fruit = fruitList[i]
            is_offscreen = fruit.update(is_frozen_now)
            if is_offscreen:
                fruitList.pop(i)
            else:
                img = fruit.draw(img)

        # C5. 绘制切割轨迹
        if trailPoints:
            for i in range(len(trailPoints) - 1):
                cv2.line(img, trailPoints[i], trailPoints[i + 1], (0, 255, 255), 10)

        # C6. 绘制分数
        cvzone.putTextRect(img, f'Score: {score}', [50, 80],
                           scale=3, thickness=3, offset=10)

        # --- ⬇️⬇️⬇️ 新增：倒计时模式逻辑 ⬇️⬇️⬇️ ---
        if gameMode == "COUNTDOWN":
            elapsed = time.time() - countdownStartTime
            remaining = max(0, countdownDuration - elapsed)
            # 在右上角显示时间
            cvzone.putTextRect(img, f'TIME: {remaining:.1f}s', [650, 80],
                               scale=3, thickness=3, offset=10)
            if remaining == 0:
                # 时间到，游戏结束
                gameState = "GAME_OVER"
        # --- ⬆️⬆️⬆️ --------------------------- ---

        # C7. 绘制冰冻效果
        if is_frozen_now:
            remaining = freezeTime - time.time()
            cvzone.putTextRect(img, f'FROZEN: {remaining:.1f}s', [300, 80],
                               scale=3, thickness=3, offset=10,
                               colorR=(0, 200, 255))

            # =================================================================
    # ------------------- 状态三：游戏结束 (GAME_OVER) -------------------
    # =================================================================
    elif gameState == "GAME_OVER":
        cvzone.putTextRect(img, "Game Over", [200, 200],
                           scale=7, thickness=5, offset=20,
                           colorR=(0, 0, 255))
        cvzone.putTextRect(img, f'Final Score: {score}', [200, 350],
                           scale=5, thickness=5, offset=20)
        # --- ⬇️⬇️⬇️ 修改：提示返回菜单 ⬇️⬇️⬇️ ---
        cvzone.putTextRect(img, "Press 'r' to return to MENU", [200, 450],
                           scale=3, thickness=3, offset=10)

    # D. 显示图像 (始终执行)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    # E. 按键处理 (始终执行)
    if key == ord('q'):
        break

    # --- ⬇️⬇️⬇️ 修改：'r' 键现在总是返回菜单 ⬇️⬇️⬇️ ---
    if key == ord('r'):
        gameState = "MENU"

# 7. 清理
print("程序退出，释放资源...")
cap.release()
cv2.destroyAllWindows()