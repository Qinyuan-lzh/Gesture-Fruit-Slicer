import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# 1. 初始化摄像头和手部检测器
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # 宽
cap.set(4, 720)  # 高


detector = HandDetector(detectionCon=0.8, maxHands=1)


# 2. ------------------- 修改后的 Fruit 类 -------------------
class Fruit:
    # <<< 添加了一个新参数 fruit_type，默认为 'fruit'
    def __init__(self, img, w, h, fruit_type='fruit'):
        self.img = img
        self.w = w
        self.h = h
        self.radius = w // 2
        self.fruit_type = fruit_type  # <<< 保存这个类型

        # 随机生成水果的起始位置和速度
        self.x = random.randint(100, 1180)
        self.y = 720

        self.vx = random.randint(-10, 10)
        self.vy = random.randint(-30, -15)
        self.gravity = 0.8

    def update(self):
        """
        更新水果位置的物理模拟
        """
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        if self.y > 720 + self.h:
            return True  # 返回True，表示可以被移除了
        return False

    def draw(self, imgMain):
        """
        在主图像上绘制水果
        """
        try:
            imgMain = cvzone.overlayPNG(imgMain, self.img,
                                        (int(self.x - self.w // 2),
                                         int(self.y - self.h // 2)))
        except:
            pass

        # <<< (可选) 绘制碰撞的圆形“热区”用于调试
        # cv2.circle(imgMain, (int(self.x), int(self.y)), self.radius, (0, 255, 0), 2)

        return imgMain


# 3. ------------------- 加载所有素材 -------------------
fruitImages = []  # <<< 用于存放所有水果图片 (img, w, h) 的列表
fruitFiles = ["orange.png", "apple.png", "pineapple.png", "watermelon.png", "banana.png",
              "Lemon.png", "durian.png", "Mango.png", "strawberry.png"]  # <<< 水果图片文件名
target_size = (100, 100)  # 统一缩放尺寸

# <<< 循环加载所有水果图片
for file in fruitFiles:
    try:
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, target_size)
        h, w, _ = img.shape
        fruitImages.append((img, w, h))  # <<< 将 (图片, 宽, 高) 元组存入列表
        print(f"成功加载: {file}")
    except Exception as e:
        print(f"错误: 无法加载 '{file}'。 {e}")

# <<< 加载炸弹图片
try:
    imgBomb = cv2.imread("bomb.png", cv2.IMREAD_UNCHANGED)
    imgBomb = cv2.resize(imgBomb, target_size)
    hBomb, wBomb, _ = imgBomb.shape
    print("成功加载: bomb.png")
except Exception as e:
    print(f"错误: 无法加载 'bomb.png'。 {e}")
    # 创建一个备用的黑色圆形作为炸弹
    imgBomb = np.zeros((100, 100, 4), dtype=np.uint8)
    cv2.circle(imgBomb, (50, 50), 40, (50, 50, 50, 255), cv2.FILLED)
    hBomb, wBomb = 100, 100

# 确保至少有一种水果加载成功
if not fruitImages:
    print("错误：没有任何水果图片加载成功！程序退出。")
    exit()

# 4. ------------------- 游戏主变量 -------------------
fruitList = []
trailPoints = []
trailLength = 15
spawnChanceFruit = 0.03  # <<< 水果生成几率
spawnChanceBomb = 0.01  # <<< 炸弹生成几率 (更低)
score = 0
gameOver = False  # <<< 新增 Game Over 状态
saved_frame = False
# 5. ------------------- 游戏主循环 -------------------
cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
while True:
    success, img = cap.read()
    if not success:
        break

    # ⬇️⬇️⬇️ 添加这部分代码 ⬇️⬇️⬇️
    # -----------------------------------------------------------
    if not saved_frame:
        # 打印图像的实际尺寸 (高, 宽, 通道数)
        print(f"图像的实际尺寸 (img.shape): {img.shape}")

        # 将这一帧保存为文件
        cv2.imwrite("frame_capture.jpg", img)
        print("已将当前帧保存为 frame_capture.jpg")

        saved_frame = True  # 确保只保存一次
    # -----------------------------------------------------------
    # ⬆️⬆️⬆️ 添加结束 ⬆️⬆️⬆️
    img = cv2.flip(img, 1)

    # A. 找到手部
    hands, img = detector.findHands(img, flipType=False)

    # <<< B. ------------------- Game Over 逻辑 -------------------
    if gameOver:
        # 如果游戏结束，显示 Game Over 画面
        cvzone.putTextRect(img, "Game Over", [300, 300],
                           scale=7, thickness=5, offset=20,
                           colorR=(0, 0, 255))  # 红色
        cvzone.putTextRect(img, f'Final Score: {score}', [300, 450],
                           scale=5, thickness=5, offset=20)
        cvzone.putTextRect(img, "Press 'r' to Restart", [300, 550],
                           scale=3, thickness=3, offset=10)

    # <<< C. ------------------- 游戏运行逻辑 -------------------
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
                        # <<< 检查切到的是水果还是炸弹
                        if fruit.fruit_type == 'fruit':
                            fruitList.pop(i)
                            score += 1
                            print(f"得分: {score}")
                            is_sliced = True
                            break
                        elif fruit.fruit_type == 'bomb':
                            # <<< 切到炸弹！
                            gameOver = True
                            is_sliced = True
                            break  # 立刻跳出内部循环

                if is_sliced:
                    if gameOver: break  # <<< 如果游戏结束，也跳出外部循环
                    continue

        else:
            trailPoints = []

        # C2. 随机生成水果
        if random.random() < spawnChanceFruit:
            # <<< 从列表中随机选一个水果
            img_f, w_f, h_f = random.choice(fruitImages)
            fruitList.append(Fruit(img_f, w_f, h_f, 'fruit'))  # <<< 指定类型

        # C3. 随机生成炸弹
        if random.random() < spawnChanceBomb:
            fruitList.append(Fruit(imgBomb, wBomb, hBomb, 'bomb'))  # <<< 指定类型为 'bomb'

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
        # <<< 重置所有游戏变量
        fruitList = []
        trailPoints = []
        score = 0
        gameOver = False

# 6. 清理
cap.release()
cv2.destroyAllWindows()