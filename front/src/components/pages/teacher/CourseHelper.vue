<template>
  <div class="container">
    <!-- 头部 -->
    <header class="header">
      <h1>课堂助手</h1>
      <button class="back-button" @click="goBack">返回</button>
    </header>

    <!-- 主内容 -->
    <div class="content">
      <div class="main-content">
        <div class="left">
          <!-- 课堂控制 -->
          <div class="classroom-controls">
            <button @click="classStarted ? endClass() : startClass()">
              {{ classStarted ? '结束课堂' : '开始课堂' }}
            </button>
            <span>{{ formattedTime }}</span>
          </div>
          
          <!-- 加载动画 -->
          <div v-if="isLoading" class="loading-spinner"></div>
          
          <!-- 视频画布 -->
          <canvas ref="canvas" class="video-canvas"></canvas>
          
          <!-- 进度条 -->
          <div class="progress-container">
            <progress :value="progress" max="100"></progress>
            <span>{{ progressText }}</span>
          </div>
        </div>
        
        <div class="right">
          <!-- 右侧上部 -->
          <div class="top">
            <div class="section">
              <h2>点答器</h2>
              <div class="button-container">
                <button @click="randomSelectStudent">随机抽取学生</button>
              </div>
            </div>
            <div class="section">
              <h2>随堂测试</h2>
              <div class="button-container">
                <button @click="openModal">AI生成题目</button>
              </div>
            </div>
          </div>
          
          <!-- 右侧下部 -->
          <div class="bottom">
            <h2>AI教育辅导</h2>
            <div class="chat-box" ref="chatBox">
              <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
                <p>{{ message.text }}</p>
              </div>
            </div>
            <div class="input-container">
              <input class="input-box" type="text" v-model="inputValue" @keypress.enter="sendMessage" placeholder="输入消息..." />
              <button class="send-button" @click="sendMessage">发送</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗 -->
    <div class="modal" v-show="isModalVisible">
      <div class="modal-content">
        <!-- 关闭按钮 -->
        <button class="close-button" @click="closeModal">
          <i class="fas fa-times"></i> <!-- 使用 Font Awesome 的关闭图标 -->
        </button>
        
        <!-- 设置题目要求 -->
        <h3>设置题目要求</h3>
        <div class="input-group">
          <label>学科：</label>
          <input type="text" v-model="questionRequirements.subject" />
        </div>
        <div class="input-group">
          <label>知识点：</label>
          <input type="text" v-model="questionRequirements.topic" />
        </div>
        <div class="input-group">
          <label>其他要求：</label>
          <input type="text" v-model="questionRequirements.other" />
        </div>
        <div class="input-group">
          <label>是否根据刚才的课堂内容生成题目：</label>
          <div>
            <button @click="selectOption(true)" :class="{ selected: questionRequirements.useClassContent === true }">是</button>
            <button @click="selectOption(false)" :class="{ selected: questionRequirements.useClassContent === false }">否</button>
          </div>
        </div>
        <button @click="generateQuestions">生成题目</button>
      </div>
    </div>
    <!-- 加载中弹窗 -->
    <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2>题目生成中...</h2>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      isLoading: false,
      isRecording: false,
      mediaRecorder: null,
      videoChunks: [],
      audioChunks: [],
      classStarted: false,
      startTime: 0,
      elapsed: 0,
      timer: null,
      messages: [
        { text: '您好，我是教育辅导AI小助手，有什么我可以帮忙的吗？', isUser: false }
      ],
      inputValue: '',
      isModalVisible: false,
      questionRequirements: {
        subject: '',
        topic: '',
        other: '',
        useClassContent: false
      },
      loading: false, // 增加loading控制生成题目弹窗
    };
  },
  computed: {
    progressText() {
      const minutes = Math.floor(this.progress * 1.2);
      return `${minutes} / 120 分钟`;
    },
    formattedTime() {
      const hours = Math.floor(this.elapsed / 3600).toString().padStart(2, '0');
      const minutes = Math.floor((this.elapsed % 3600) / 60).toString().padStart(2, '0');
      const seconds = (this.elapsed % 60).toString().padStart(2, '0');
      return `${hours}:${minutes}:${seconds}`;
    },
  },
  methods: {
    async startClass() {
      this.classStarted = true;
      this.startTime = Date.now();
      this.timer = setInterval(() => {
        this.elapsed = Math.floor((Date.now() - this.startTime) / 1000);
      }, 1000);
      await this.startRecording();
    },
    async endClass() {
      this.classStarted = false;
      clearInterval(this.timer);
      await this.stopRecording();
    },
    async startRecording() {
      this.isLoading = true;
      this.videoChunks = [];
      this.audioChunks = [];

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        
        this.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            if (e.data.type.includes('video')) {
              this.videoChunks.push(e.data);
            } else {
              this.audioChunks.push(e.data);
            }
          }
        };

        this.mediaRecorder.onstop = this.saveRecording;
        this.mediaRecorder.start();

        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.play();

        videoElement.addEventListener('loadedmetadata', () => {
          this.isLoading = false;
          this.drawVideoFrame(videoElement);
        });

      } catch (err) {
        console.error("Error accessing the camera or microphone", err);
        this.isLoading = false;
      }
    },
    async stopRecording() {
      this.isRecording = false;
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
        // Stop the tracks of the media stream
        const stream = this.mediaRecorder.stream;
        if (stream) {
          stream.getTracks().forEach(track => {
            track.stop();
          });
        }
      }
    },
    drawVideoFrame(videoElement) {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;

      const draw = () => {
        if (!this.classStarted) return;

        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        requestAnimationFrame(draw);
      };
      draw();
    },
    saveRecording() {
      const videoBlob = new Blob(this.videoChunks, { type: 'video/webm' });
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

      // Use IndexedDB to store the recordings
      const dbRequest = indexedDB.open('classroomRecordings', 1);

      dbRequest.onupgradeneeded = function(event) {
        const db = event.target.result;
        db.createObjectStore('videos', { autoIncrement: true });
        db.createObjectStore('audios', { autoIncrement: true });
      };

      dbRequest.onsuccess = function(event) {
        const db = event.target.result;
        const videoTransaction = db.transaction('videos', 'readwrite');
        const audioTransaction = db.transaction('audios', 'readwrite');

        const videoStore = videoTransaction.objectStore('videos');
        const audioStore = audioTransaction.objectStore('audios');

        videoStore.add(videoBlob);
        audioStore.add(audioBlob);

        videoTransaction.oncomplete = function() {
          console.log('Video saved to IndexedDB');
        };

        audioTransaction.oncomplete = function() {
          console.log('Audio saved to IndexedDB');
        };
      };

      dbRequest.onerror = function(event) {
        console.error('Error opening IndexedDB', event.target.errorCode);
      };
    },
    randomSelectStudent() {
      // 随机抽取学生逻辑
    },
    openModal() {
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    selectOption(option) {
      this.questionRequirements.useClassContent = option;
    },
    generateQuestions() {
      this.loading = true;
      // Prepare data to send to backend
      const requestData = {
        subjects: [
          this.questionRequirements.subject || '',
          this.questionRequirements.topic || this.questionRequirements.subject
        ],
        time: 10, // Example time in minutes
        min_difficulty: 3,
        max_difficulty: 8,
        type: ["single_choice", "judgement",'fillin'],
        others: this.questionRequirements.other
      };
      console.log("requestData:",requestData);
      axios.post('http://localhost:5000/get_ClassTestProblems', requestData)
        .then((res) => {
          console.log("res.data['problems']:",(res.data)['problems']);
          // Save the received questions to IndexedDB
          this.saveQuestionsToIndexedDB((res.data)['problems']);
          this.closeModal(); // Close modal after successful operation
        })
        .catch((err) => {
          console.error('Error generating questions:', err);
          // Optionally handle error display or logging
        });
    },
    async saveQuestionsToIndexedDB(problems) {
      const db = await openDB('ClassTestProblems', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('single_choice')) {
            db.createObjectStore('single_choice', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('judgement')) {
            db.createObjectStore('judgement', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('fillin')) {
            db.createObjectStore('fillin', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('evaluation')) {
            console.log("no evaluation")
            db.createObjectStore('evaluation', { keyPath: 'id', autoIncrement: true });
          }
          console.log('evaluation')
          if (!db.objectStoreNames.contains('dimension')) {
            db.createObjectStore('dimension', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('score')) {
            db.createObjectStore('score', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('shortcoming')) {
            db.createObjectStore('shortcoming', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('suggestion')) {
            db.createObjectStore('suggestion', { keyPath: 'id', autoIncrement: true });
          }
        },
    });

    // Start a new transaction to clear existing data
    const tx = db.transaction(['single_choice', 'judgement', 'fillin'], 'readwrite');
    await Promise.all([
      tx.objectStore('single_choice').clear(),
      tx.objectStore('judgement').clear(),
      tx.objectStore('fillin').clear(),
    ]);
    await tx.done;

    // Start a new transaction to store new problems
    const txNew = db.transaction(['single_choice', 'judgement', 'fillin'], 'readwrite');
    let singleChoiceId = 1;
    let judgementId = 1;
    let fillinId = 1;

    problems.forEach((problem) => {
      const problemWithDoneAnswer = { ...problem, doneanswer: '' };
      if (problem.type === 'single_choice') {
        txNew.objectStore('single_choice').put({ ...problemWithDoneAnswer, id: singleChoiceId++ });
      } else if (problem.type === 'judgement') {
        txNew.objectStore('judgement').put({ ...problemWithDoneAnswer, id: judgementId++ });
      } else if (problem.type === 'fillin') {
        txNew.objectStore('fillin').put({ ...problemWithDoneAnswer, id: fillinId++ });
      }
    });
    await txNew.done;
    console.log('随堂测试题目存储完毕');
    this.loading = false;
    this.$router.push('/classtest');
    },
    sendMessage() {
      if (this.inputValue.trim() === '') return;
      this.messages.push({ text: this.inputValue, isUser: true });
      const userMessage = this.inputValue;
      this.inputValue = '';

      axios.post('http://127.0.0.1:5000/api/reply', {
        message: userMessage
      })
      .then((res) => {
        this.messages.push({ text: res.data.reply, isUser: false });
      })
      .catch((err) => {
        console.error(err);
      });
    },
    goBack() {
      this.$router.back();
    }
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
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
}

.classroom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #ffffff;
  border-bottom: 1px solid #ffffff;

  button {
    padding: 0.5rem 1rem;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  span {
    font-size: 1.2rem;
    font-weight: bold;
  }
}

.main-content {
  display: flex;
  flex: 1;
}

.left {
  flex: 3;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  border-right: 1px solid #ddd;
  border: 2px solid black;
  margin: 10px;
  padding: 10px;
  position: relative;

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
    margin-top: 10px;
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

    .section {
      display: flex;
      flex-direction: column;
      align-items: flex-start;

      h2 {
        margin: 0 0 1rem 0;
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
  }

  .bottom {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    border: 2px solid black;

    h2 {
      margin: 0 0 1rem 0;
    }

    .chat-box {
      flex: 3;
      padding: 10px;
      overflow-y: scroll;
    }

    .input-container {
      display: flex;
      align-items: center;
      padding: 10px;
      background-color: #fff;
      border-top: 1px solid #ccc;
    }

    .input-box {
      flex: 1;
      height: 40px;
      border: 1px solid #ccc;
      border-radius: 5px;
      padding: 5px;
    }

    .send-button {
      margin-left: 10px;
      padding: 10px;
      background-color: #1890ff;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    .message {
      margin-bottom: 10px;
      padding: 10px;
      border-radius: 5px;
      background-color: #fff;
      max-width: 70%;
    }

    .user-message {
      align-self: flex-end;
      background-color: #d1f0d1;
    }
  }
}

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
  max-width: 90%;
  text-align: center;
  position: relative; /* Ensure relative positioning for child elements */
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  margin-right: 10px;
}

.input-group input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.input-group div {
  margin-top: 0.5rem;
}

.selected {
  background-color: #007bff;
  color: #fff;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 加载中弹窗样式 */
.loading-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .loading-content {
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
  }
</style>
