import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time  # <<< 1. 导入 time 库

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

# X 轴 (水平) 裁切
crop_x_start = 160
crop_x_end = 1120  # 160 + 960
new_width = 960  # 裁切后的真实宽度

# Y 轴 (垂直) 裁切
crop_y_start = 72
crop_y_end = 648  # 72 + 576
new_height = 576  # 裁切后的真实高度

# 创建一个可调整大小的窗口
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
# 强制将窗口大小设置为 *最终* 的大小
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


# 3. ------------------- 修改后的 Fruit 类 -------------------
class Fruit:
    # <<< 3. 添加 image_name 参数
    def __init__(self, img, w, h, fruit_type='fruit', image_name="unknown"):
        self.img = img
        self.w = w
        self.h = h
        self.radius = w // 2
        self.fruit_type = fruit_type
        self.image_name = image_name  # <<< 保存图片名

        self.x = random.randint(100, new_width - 100)
        self.y = new_height
        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-30, -15)
        self.gravity = 0.8

    # <<< 3. 添加 is_frozen 参数
    def update(self, is_frozen=False):

        if is_frozen:
            # --- 冰冻状态：速度减慢 ---
            self.vy += self.gravity * 0.1  # 重力效果大大减弱
            self.x += self.vx * 0.1  # 水平速度减慢
            self.y += self.vy * 0.1  # 垂直速度减慢
        else:
            # --- 正常状态 ---
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
# <<< 2. 使用你的新水果列表
fruitFiles = ["orange.png", "apple.png", "pineapple.png", "watermelon.png", "banana.png",
              "Lemon.png", "durian.png", "Mango.png", "strawberry.png"]
target_size = (100, 100)

for file in fruitFiles:
    try:
        img = cv_imread_chinese(file)
        if img is None:
            raise ValueError("图片加载后仍为 None")
        img = cv2.resize(img, target_size)
        h, w, _ = img.shape
        # <<< 2. 保存 (img, w, h, file_name)
        fruitImages.append((img, w, h, file))
        print(f"成功加载: {file}")
    except Exception as e:
        print(f"错误: 无法加载 '{file}'。 {e}")

# ... (加载炸弹的代码不变) ...
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
spawnChanceBomb = 0.01
score = 0
gameOver = False

# <<< 4. 添加冰冻效果的变量
freezeTime = 0.0  # 冰冻效果结束的时间戳
freezeDuration = 3.0  # 冰冻持续 3 秒

# 6. ------------------- 游戏主循环 -------------------
while True:
    success, img = cap.read()
    if not success:
        break

    # --- 裁切黑边 ---
    img = img[crop_y_start:crop_y_end, crop_x_start:crop_x_end]

    # --- 翻转 ---
    img = cv2.flip(img, 1)

    # A. 找到手部
    hands, img = detector.findHands(img, flipType=False)

    # --- 检查当前是否处于冰冻状态 ---
    is_frozen_now = time.time() < freezeTime

    # B. Game Over 逻辑
    if gameOver:
        cvzone.putTextRect(img, "Game Over", [200, 200], scale=7, thickness=5, offset=20, colorR=(0, 0, 255))
        cvzone.putTextRect(img, f'Final Score: {score}', [200, 350], scale=5, thickness=5, offset=20)
        cvzone.putTextRect(img, "Press 'r' to Restart", [200, 450], scale=3, thickness=3, offset=10)

    # C. 游戏运行逻辑
    else:
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

                            # <<< 5. 检查是否切到了柠檬
                            if fruit.image_name == "Lemon.png":
                                print("--- 柠檬！触发冰冻！---")
                                # 设置冰冻结束时间为 "当前时间 + 持续时间"
                                freezeTime = time.time() + freezeDuration

                            break
                        elif fruit.fruit_type == 'bomb':
                            gameOver = True
                            is_sliced = True
                            break

                if is_sliced:
                    if gameOver: break
                    continue
        else:
            trailPoints = []

        # C2. 随机生成水果 (只在非冰冻时生成，避免卡顿)
        if not is_frozen_now:
            if random.random() < spawnChanceFruit:
                # <<< 3. 传入文件名
                img_f, w_f, h_f, file_name = random.choice(fruitImages)
                fruitList.append(Fruit(img_f, w_f, h_f, 'fruit', file_name))

            if random.random() < spawnChanceBomb:
                fruitList.append(Fruit(imgBomb, wBomb, hBomb, 'bomb', "bomb.png"))

        # C4. 更新和绘制水果
        for i in range(len(fruitList) - 1, -1, -1):
            fruit = fruitList[i]
            # <<< 6. 传入冰冻状态
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

        # <<< 7. 绘制冰冻视觉效果
        if is_frozen_now:
            remaining = freezeTime - time.time()
            cvzone.putTextRect(img, f'FROZEN: {remaining:.1f}s', [300, 80],
                               scale=3, thickness=3, offset=10,
                               colorR=(0, 200, 255))  # 淡蓝色

    # D. 显示图像
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    # E. 按 'q' 退出, 按 'r' 重置
    if key == ord('q'):
        break
    if key == ord('r'):
        fruitList = []
        trailPoints = []
        score = 0
        gameOver = False
        freezeTime = 0.0  # 重置冰冻时间

# 7. 清理
print("程序退出，释放资源...")
cap.release()
cv2.destroyAllWindows()