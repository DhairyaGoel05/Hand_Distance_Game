import random
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import math
import cvzone
import time

# WEBCAM
cap = cv2.VideoCapture(0)
cap.set(3, 1200)
cap.set(4, 720)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)  # Support for 2 players

# Find Function
# distances is the distance and values is the value in cm
distances = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
values = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(distances, values, 2)

# Game Variables
cx, cy = 250, 250
color = (255, 0, 255)
counter = 0
score = 0
timeStart = time.time()
totalTime = 20
level = 1

# Power-ups and Obstacles
powerUps = []
obstacles = []

def add_power_up():
    powerUps.append((random.randint(100, 1100), random.randint(100, 600)))

def add_obstacle():
    obstacles.append((random.randint(100, 1100), random.randint(100, 600)))

add_power_up()
add_obstacle()

# Loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=False)

    if time.time() - timeStart < totalTime:
        if hands:
            for hand in hands:
                lmList = hand['lmList']
                hand_bbox = hand['bbox']
                hx, hy, hw, hh = hand_bbox
                x1, y1, _ = lmList[5]
                x2, y2, _ = lmList[17]
                distance = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                A, B, C = coff
                distanceCm = A * distance ** 2 + B * distance + C

                print(distanceCm, distance)

                if distanceCm < 40:
                    if hx < cx < hx + hw and hy < cy < hy + hh:
                        counter = 1

                cv2.rectangle(img, (hx, hy), (hx + hw, hy + hh), (255, 0, 255), 3)
                cvzone.putTextRect(img, f'{int(distanceCm)} cm', (hx + 5, hy - 10))

                if counter:
                    counter += 1
                    color = (0, 255, 0)
                    if counter == 3:
                        cx = random.randint(100, 1100)
                        cy = random.randint(100, 600)
                        color = (255, 0, 255)
                        score += 1
                        counter = 0
                        if score % 5 == 0:
                            level += 1
                            add_power_up()
                            add_obstacle()

        # Draw Button
        cv2.circle(img, (cx, cy), 30, color, cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2)
        cv2.circle(img, (cx, cy), 30, (50, 50, 50), 2)

        # Draw Power-ups and Obstacles
        for px, py in powerUps:
            cv2.circle(img, (px, py), 20, (0, 255, 255), cv2.FILLED)
            if any(hand['bbox'][0] < px < hand['bbox'][0] + hand['bbox'][2] and
                   hand['bbox'][1] < py < hand['bbox'][1] + hand['bbox'][3] for hand in hands):
                score += 5
                powerUps.remove((px, py))

        for ox, oy in obstacles:
            cv2.circle(img, (ox, oy), 20, (0, 0, 255), cv2.FILLED)
            if any(hand['bbox'][0] < ox < hand['bbox'][0] + hand['bbox'][2] and
                   hand['bbox'][1] < oy < hand['bbox'][1] + hand['bbox'][3] for hand in hands):
                score -= 5
                obstacles.remove((ox, oy))

        # Game HUD
        cvzone.putTextRect(img, f'Time: {int(totalTime - (time.time() - timeStart))}', (900, 50), scale=3, offset=10, colorR=(0, 0, 0), colorT=(255, 255, 255))
        cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (50, 50), scale=3, offset=10, colorR=(0, 0, 0), colorT=(255, 255, 255))
        cvzone.putTextRect(img, f'Level: {level}', (500, 50), scale=3, offset=10, colorR=(0, 0, 0), colorT=(255, 255, 255))
    else:
        cvzone.putTextRect(img, 'Game Over', (400, 300), scale=5, offset=20, colorR=(0, 0, 0), colorT=(255, 0, 0))

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # To break the loop by pressing 'q'
        break

cap.release()
cv2.destroyAllWindows()
