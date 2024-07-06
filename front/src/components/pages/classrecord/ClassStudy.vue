<template>
    <div class="container">
      <header class="header">
        <h1>课程学习</h1>
        <button class="back-button" @click="goBack">返回</button>
      </header>
      <div class="content">
        <div class="left">
          <h2 class="left-title">课程内容</h2>
          <div v-if="isLoading" class="loading-spinner"></div>
          <canvas ref="canvas" class="video-canvas"></canvas>
          <div class="progress-container">
            <progress :value="progress" max="100"></progress>
            <span>{{ progressText }}</span>
          </div>
        </div>
        <div class="right">
          <div class="top">
            <h2>课程概述</h2>
            <textarea ref="courseDescription" :value="courseDescription" @input="updateCourseDescription"></textarea>
          </div>
          <div class="bottom">
            <h2>AI随时问答</h2>
            <div class="chat-container">
              <div class="messages" ref="messages">
                <div v-for="(message, index) in chatMessages" :key="index" :class="['message', message.sender]">
                  <div class="message-text">{{ message.text }}</div>
                </div>
              </div>
              <div class="input-container">
                <textarea v-model="newMessage" placeholder="输入提问" @keydown.enter.prevent="sendMessage"></textarea>
                <button @click="sendMessage">发送</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  data() {
    return {
      isLoading: false,
      isRecording: false,
      isUploading: false,
      lastFrame: null,
      mediaStream: null,
      video: null,
      progress: 0,
      recordingStartTime: null,
      courseDescription: "课程概述内容",
      chatMessages: [
        { text: "您好，我是AI问答助手，您对于课程内容有什么不懂的地方请随时问我。", sender: "ai" }
      ],
      newMessage: ""
    };
  },
  computed: {
    progressText() {
      const minutes = Math.floor(this.progress * 1.2);
      return `${minutes} / 120 分钟`;
    }
  },
  methods: {
    async toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    },
    async startRecording() {
      this.isRecording = true;
      this.isLoading = true;
      this.progress = 0;
      this.recordingStartTime = Date.now();

      try {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.video = document.createElement('video');
        this.video.srcObject = this.mediaStream;
        this.video.play();

        this.video.addEventListener('loadedmetadata', () => {
          this.isLoading = false;
          this.drawVideoFrame();
          this.updateProgress();
        });
      } catch (err) {
        console.error("Error accessing the camera", err);
        this.isLoading = false;
      }
    },
    stopRecording() {
      this.isRecording = false;
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
      }
      this.captureLastFrame();
    },
    drawVideoFrame() {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      canvas.width = this.video.videoWidth;
      canvas.height = this.video.videoHeight;

      const draw = () => {
        if (!this.isRecording) return;

        context.drawImage(this.video, 0, 0, canvas.width, canvas.height);
        requestAnimationFrame(draw);
      };
      draw();
    },
    captureLastFrame() {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      context.drawImage(this.video, 0, 0, canvas.width, canvas.height);
      this.lastFrame = canvas.toDataURL('image/png');
    },
    updateProgress() {
      if (!this.isRecording) return;

      const elapsedTime = (Date.now() - this.recordingStartTime) / 1000; // elapsed time in seconds
      const progressPercentage = Math.min((elapsedTime / (120 * 60)) * 100, 100);
      this.progress = progressPercentage;

      if (progressPercentage < 100) {
        requestAnimationFrame(this.updateProgress);
      }
    },
    uploadRecording() {
      // 上传录课逻辑
    },
    startUploading() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        const url = URL.createObjectURL(file);
        this.loadVideoFrame(url);
      }
    },
    loadVideoFrame(url) {
      const video = document.createElement('video');
      video.src = url;
      video.addEventListener('loadeddata', () => {
        const canvas = this.$refs.canvas;
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        this.lastFrame = canvas.toDataURL('image/png');
        URL.revokeObjectURL(url); // 释放对象URL
      });
      video.addEventListener('error', (e) => {
        console.error('Error loading video file', e);
      });
    },
    uploadLocalCourse() {
      // 上传本地课程逻辑
    },
    generateAIDescription() {
      // 生成AI概述逻辑
    },
    startManualEdit() {
      const textarea = this.$refs.courseDescription;
      textarea.focus();
      textarea.setSelectionRange(0, 0); // 将光标置于文本框开头
    },
    updateCourseDescription(event) {
      this.courseDescription = event.target.value;
    },
    sendMessage() {
      if (this.newMessage.trim() === "") return;

      this.chatMessages.push({ text: this.newMessage, sender: "user" });
      this.newMessage = "";

      // 模拟AI响应
      setTimeout(() => {
        this.chatMessages.push({ text: "这是AI的响应。", sender: "ai" });
        this.scrollToBottom();
      }, 1000);
    },
    scrollToBottom() {
      const messages = this.$refs.messages;
      messages.scrollTop = messages.scrollHeight;
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>
<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 97vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;

  h1 {
    margin: 0;
  }

  .back-button {
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
}

.content {
  display: flex;
  flex: 1;

  .left {
    flex: 3;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border-right: 1px solid #ddd;
    border: 2px solid black;
    margin: 10px;
    padding: 10px;
    position: relative;

    .left-title {
      position: absolute;
      top: 10px;
      left: 10px;
      z-index: 1;
    }

    .loading-spinner {
      width: 50px;
      height: 50px;
      border: 5px solid #f3f3f3;
      border-top: 5px solid #007bff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    canvas.video-canvas {
      width: 70%;
      height: auto;
      border: 1px solid #000;
      display: block;
      z-index: 0;
    }

    img {
      width: 70%;
      height: auto;
      border: 1px solid #000;
    }

    .progress-container {
      width: 70%;
      position: absolute;
      bottom: 10px;
      text-align: center;

      progress {
        width: 100%;
        height: 20px;
        border: 1px solid #000;
        border-radius: 4px;
      }

      span {
        display: block;
        margin-top: 5px;
        font-size: 1rem;
        color: #333;
      }
    }
  }

  .right {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem;

    .top {
      display: flex;
      flex-direction: column;
      gap: 1rem;

      h2 {
        margin: 0 0 1rem 0;
      }

      textarea {
        border: 1px solid black;
        width: 100%;
        padding: 0.5rem;
        border-radius: 4px;
        resize: none;
        height: 100%;
      }

      .button-container {
        display: flex;
        gap: 1rem;

        button {
          padding: 0.5rem 1rem;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
      }
    }

    .bottom {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      flex: 1;

      h2 {
        margin: 0 0 1rem 0;
      }

      .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        border: 1px solid black;
        border-radius: 4px;
        overflow: hidden;

        .messages {
          flex: 1;
          padding: 1rem;
          overflow-y: auto;
          background-color: #f9f9f9;

          .message {
            display: flex;
            margin-bottom: 1rem;

            &.user {
              justify-content: flex-end;

              .message-text {
                background-color: #007bff;
                color: white;
              }
            }

            &.ai {
              justify-content: flex-start;

              .message-text {
                background-color: #f1f1f1;
                color: black;
              }
            }

            .message-text {
              padding: 0.5rem 1rem;
              border-radius: 4px;
              max-width: 70%;
              word-wrap: break-word;
            }
          }
        }

        .input-container {
          display: flex;
          padding: 1rem;
          background-color: #fff;
          border-top: 1px solid #ddd;

          textarea {
            flex: 1;
            border: 1px solid black;
            padding: 0.5rem;
            border-radius: 4px;
            resize: none;
          }

          button {
            margin-left: 1rem;
            padding: 0.5rem 1rem;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
          }
        }
      }
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
