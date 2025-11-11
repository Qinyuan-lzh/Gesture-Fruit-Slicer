import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# 1. 初始化摄像头和手部检测器
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # 宽 (请求 16:9)
cap.set(4, 720)  # 高 (请求 16:9)

# -----------------------------------------------------------
# -- 黑边裁切 解决方案 --
# -----------------------------------------------------------
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"摄像头实际分辨率: {width} x {height} (带黑边)")

# --- ⬇️⬇️⬇️ 已修改 ⬇️⬇️⬇️ ---
# X 轴 (水平) 裁切
crop_x_start = 160
crop_x_end = 1120  # 160 + 960
new_width = 960  # 裁切后的真实宽度

# Y 轴 (垂直) 裁切
crop_y_start = 72
crop_y_end = 648  # 72 + 576
new_height = 576  # 裁切后的真实高度
# --- ⬆️⬆️⬆️ 修改结束 ⬆️⬆️⬆️ ---

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
    def __init__(self, img, w, h, fruit_type='fruit'):
        self.img = img
        self.w = w
        self.h = h
        self.radius = w // 2
        self.fruit_type = fruit_type

        # X 坐标：在 960 宽度内随机
        self.x = random.randint(100, new_width - 100)

        # --- ⬇️⬇️⬇️ 已修改 ⬇️⬇️⬇️ ---
        # Y 坐标：从 *新高度* (576) 的底部开始
        self.y = new_height
        # --- ⬆️⬆️⬆️ 修改结束 ⬆️⬆️⬆️ ---

        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-30, -15)  # 保持向上的初速度
        self.gravity = 0.8

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        # --- ⬇️⬇️⬇️ 已修改 ⬇️⬇️⬇️ ---
        # 检查是否掉出 *新高度* (576) 的屏幕
        if self.y > new_height + self.h:
            # --- ⬆️⬆️⬆️ 修改结束 ⬆️⬆️⬆️ ---
            return True  # 返回True，表示可以被移除了
        return False

    def draw(self, imgMain):
        try:
            # 这个函数是相对于 imgMain (已裁切图像) 绘制的，所以 self.x, self.y 无需更改
            imgMain = cvzone.overlayPNG(imgMain, self.img,
                                        (int(self.x - self.w // 2),
                                         int(self.y - self.h // 2)))
        except:
            pass
        return imgMain


# 4. ------------------- 加载所有素材 -------------------
fruitImages = []
fruitFiles = ["orange.png", "apple.png", "pineapple.png", "watermelon.png", "banana.png",
              "Lemon.png", "durian.png", "Mango.png", "strawberry.png"]  # <<< 水果图片文件名
target_size = (100, 100)

for file in fruitFiles:
    try:
        img = cv_imread_chinese(file)
        if img is None:
            raise ValueError("图片加载后仍为 None")
        img = cv2.resize(img, target_size)
        h, w, _ = img.shape
        fruitImages.append((img, w, h))
        print(f"成功加载: {file}")
    except Exception as e:
        print(f"错误: 无法加载 '{file}'。 {e}")

try:
    imgBomb = cv_imread_chinese("bomb.png")
    if imgBomb is None:
        raise ValueError("炸弹图片加载失败")
    imgBomb = cv2.resize(imgBomb, target_size)
    hBomb, wBomb, _ = imgBomb.shape
    print("成功加载: bomb.png")
except Exception as e:
    print(f"错误: 无法加载 'bomb.png'。 {e}")
    imgBomb = np.zeros((100, 100, 4), dtype=np.uint8)
    cv2.circle(imgBomb, (50, 50), 40, (50, 50, 50, 255), cv2.FILLED)
    hBomb, wBomb = 100, 100

if not fruitImages:
    print("错误：没有任何水果图片加载成功！程序退出。")
    exit()

# 5. ------------------- 游戏主变量 -------------------
fruitList = []
trailPoints = []
trailLength = 15
spawnChanceFruit = 0.03
spawnChanceBomb = 0.01
score = 0
gameOver = False

# 6. ------------------- 游戏主循环 -------------------
while True:
    success, img = cap.read()
    if not success:
        break

    # -----------------------------------------------------------
    # -- 关键修复：使用新的 Y 坐标进行裁切！ --
    # --- ⬇️⬇️⬇️ 已修改 ⬇️⬇️⬇️ ---
    # img[y_start:y_end, x_start:x_end]
    img = img[crop_y_start:crop_y_end, crop_x_start:crop_x_end]
    # --- ⬆️⬆️⬆️ 修改结束 ⬆️⬆️⬆️ ---
    # -----------------------------------------------------------

    # 翻转摄像头 (现在是对 960x576 的图像操作)
    img = cv2.flip(img, 1)

    # A. 找到手部
    hands, img = detector.findHands(img, flipType=False)

    # B. Game Over 逻辑
    if gameOver:
        # --- ⬇️⬇️⬇️ (可选) 调整了 Y 坐标以适应 576 高度 ---
        cvzone.putTextRect(img, "Game Over", [200, 200],
                           scale=7, thickness=5, offset=20,
                           colorR=(0, 0, 255))
        cvzone.putTextRect(img, f'Final Score: {score}', [200, 350],
                           scale=5, thickness=5, offset=20)
        cvzone.putTextRect(img, "Press 'r' to Restart", [200, 450],
                           scale=3, thickness=3, offset=10)

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

        # C2. 随机生成水果
        if random.random() < spawnChanceFruit:
            img_f, w_f, h_f = random.choice(fruitImages)
            fruitList.append(Fruit(img_f, w_f, h_f, 'fruit'))

        # C3. 随机生成炸弹
        if random.random() < spawnChanceBomb:
            fruitList.append(Fruit(imgBomb, wBomb, hBomb, 'bomb'))

        # C4. 更新和绘制水果
        for i in range(len(fruitList) - 1, -1, -1):
            fruit = fruitList[i]
            is_offscreen = fruit.update()

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

# 7. 清理
print("程序退出，释放资源...")
cap.release()
cv2.destroyAllWindows()