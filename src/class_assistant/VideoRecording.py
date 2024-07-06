import cv2
import time

"""
需要等待20s左右才能开始视频录制
"""


def record_video(resolution=(1920, 1080), fps=30, codec='XVID', record_time=3600):
    cap = cv2.VideoCapture(0)

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # 定义编解码器并创建 VideoWriter 对象
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter('audio/output.avi', fourcc, fps, resolution)

    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("无法获取画面，退出...")
            break

        out.write(frame)

        # 显示正在录制的视频画面
        cv2.imshow('Recording...', frame)

        # 计算已经录制的时间
        elapsed_time = time.time() - start_time

        # 如果按 'q' 键或达到预定时间则停止录制
        # TODO 这里在前端选择结束
        if cv2.waitKey(1) & 0xFF == ord('q') or elapsed_time >= record_time:
            print(f"录制结束，已录制时长：{int(elapsed_time)}秒")
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    #
    #   resolution = (,)
    #   fps =
    #  TODO 需要在前端设置正确的分辨率和帧率和时间（时间在1-3600）可以不选择（一直录制）
    record_video(record_time=10)
