<template>
    <div class="container">
      <div class="header">
        <h1 class="title">AI教育辅导</h1>
        <div class="back-button" @click="goBack">返回</div>
      </div>
      <div class="content">
        <div class="chat-box" ref="chatBox">
          <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
            <p>{{ message.text }}</p>
          </div>
        </div>
        <div class="sidebar">
          <div class="sidebar-content">
            <h2 class="sidebar-title">历史问题</h2>
            <div v-for="(question, index) in questions" :key="index" class="question-item">
              <p>{{ question }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="input-container">
        <input class="input-box" type="text" v-model="inputValue" @keypress.enter="sendMessage" placeholder="输入消息..." />
        <button class="send-button" @click="sendMessage">发送</button>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        messages: [
          { text: '您好，我是教育辅导AI小助手，有什么我可以帮忙的吗？', isUser: false }
        ],
        questions: [],
        inputValue: ''
      };
    },
    methods: {
      sendMessage() {
        if (this.inputValue.trim() === '') return;
        this.messages.push({ text: this.inputValue, isUser: true });
        this.questions.push(this.inputValue);
        const userMessage = this.inputValue;
        this.inputValue = '';
        
        // 向后端发送请求
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
    }
  };
  </script>
  
  
  <style lang="scss" scoped>
  .container {
    background-image: url("https://bpic.588ku.com/back_pic/19/03/25/e99eca2587d8c5c78feddad37168cb01.jpg");
    background-repeat: no-repeat;
    background-size: cover;
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f5f5f5;
  }
  
  .header {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    padding: 10px;
    background-color: #aaffff;
    border-bottom: 1px solid #ccc;
    position: relative;
    margin-top: 10px; /* 调整标题距离顶部的距离 */
    }

  
  .title {
    font-size: 26px;
    font-weight: bold;
  }
  
  .back-button {
  font-weight: bold;
  position: absolute;
  right: 30px;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #080b0d;
  padding: 8px 12px; /* 添加内边距 */
  border: 1px solid #080b0d; /* 添加边框 */
  border-radius: 5px; /* 添加圆角 */
  background-color: transparent; /* 使背景透明 */
  transition: all 0.3s ease; /* 添加过渡效果 */
}

.back-button:hover {
  background-color: #080b0d; /* 鼠标悬停时改变背景颜色 */
  color: #fff; /* 鼠标悬停时改变文字颜色 */
}

  
  .content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  
  .chat-box {
    flex: 3;
    padding: 10px;
    overflow-y: scroll;
  }
  
  .sidebar {
    flex: 1;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.8);
    overflow-y: hidden;
  }
  
  .sidebar-content {
    text-align: center;
  }
  
  .sidebar-title {
    font-weight: bold;
    margin-bottom: 10px;
  }
  
  .question-item {
    margin-bottom: 10px;
    padding: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
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
  </style>
  