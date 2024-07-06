<template>
  <div class="file-uploader">
    <!-- Page Title -->
    <div class="page-title">
      <h1>PPT生成</h1>
    </div>

    <!-- Content Section -->
    <div class="content">
      <!-- Left Section -->
      <div class="left-section">
        <div class="upload-section">
          <button @click="triggerFileUpload"><i class="fas fa-upload"></i> 上传文件</button>
          <input type="file" ref="fileInput" @change="handleFileUpload" accept=".pdf,.doc,.docx,.txt" style="display: none;" />
        </div>
        <textarea v-if="!fileContent" readonly class="placeholder-textarea" placeholder="文件主要内容">文件主要内容</textarea>
        <textarea v-else v-model="fileContent" readonly placeholder="文件主要内容"></textarea>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <div class="generate-section">
          <button @click="showThemeDialog"><i class="fas fa-file-download"></i> 生成PPT</button>
        </div>
        <textarea v-if="!pptContent" readonly class="placeholder-textarea" placeholder="PPT生成结果">PPT生成结果</textarea>
        <textarea v-else v-model="pptContent" readonly placeholder="PPT生成结果"></textarea>
      </div>
    </div>

    <!-- Theme Selection Dialog -->
    <div v-if="showDialog" class="theme-dialog">
      <div class="theme-dialog-content">
        <h2>PPT具体需求</h2>
        
        <!-- PPT Style Section -->
        <h3>PPT风格</h3>
        <div class="theme-buttons">
          <button @click="selectTheme('auto')" :class="{ selected: selectedTheme === 'auto' }">自动</button>
          <button @click="selectTheme('purple')" :class="{ selected: selectedTheme === 'purple' }">紫色主题</button>
          <button @click="selectTheme('green')" :class="{ selected: selectedTheme === 'green' }">绿色主题</button>
          <button @click="selectTheme('lightblue')" :class="{ selected: selectedTheme === 'lightblue' }">清逸天蓝</button>
        </div>
        <div class="theme-buttons">
          <button @click="selectTheme('taupe')" :class="{ selected: selectedTheme === 'taupe' }">质感之境</button>
          <button @click="selectTheme('blue')" :class="{ selected: selectedTheme === 'blue' }">星光夜影</button>
          <button @click="selectTheme('telecomRed')" :class="{ selected: selectedTheme === 'telecomRed' }">炽热暖阳</button>
          <button @click="selectTheme('telecomGreen')" :class="{ selected: selectedTheme === 'telecomGreen' }">幻翠奇旅</button>
        </div>
        
        <!-- PPT Notes Section -->
        <h3>是否需要备注</h3>
        <div class="notes-buttons">
          <button @click="selectNotesOption(1)" :class="{ selected: notesOption === 1 }">
            <span class="radio-button"><i class="fas fa-circle-notch" :class="{ 'fa-check-circle': notesOption === 1 }"></i></span> 是
          </button>
          <button @click="selectNotesOption(0)" :class="{ selected: notesOption === 0 }">
            <span class="radio-button"><i class="fas fa-circle-notch" :class="{ 'fa-check-circle': notesOption === 0 }"></i></span> 否
          </button>
        </div>
        
        <!-- Generate PPT Button -->
        <div class="generate-ppt-button">
          <button @click="uploadFile"><i class="fas fa-file-powerpoint"></i> 开始生成PPT</button>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <button class="back-button" @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
  </div>
</template>
<script>
import axios from 'axios'; // 引入 axios 库
import PptxGenJS from 'pptxgenjs';

export default {
  data() {
    return {
      fileContent: '', // 存储文件主要内容
      showDialog: false, // 控制主题选择弹窗显示
      selectedTheme: 'auto', // 存储选择的主题
      selectedFile: null, // 存储上传的文件
      notesOption: 0, // 存储选择的备注选项，默认值为0,不生成
      pptContent: '' // 存储PPT生成结果
    };
  },
  methods: {
    showThemeDialog() {
      this.showDialog = true; // 显示主题选择弹窗
    },
    selectTheme(theme) {
      this.selectedTheme = theme;
    },
    selectNotesOption(option) {
      this.notesOption = option;
    },
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file; // 存储选中的文件
        const reader = new FileReader();
        reader.onload = (e) => {
          this.fileContent = e.target.result;
        };
        reader.readAsText(file); // 这里只读取文本文件内容
      }
    },
    async uploadFile() {
      if (!this.selectedFile) {
        alert("请先上传文件！");
        return;
      }

      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('theme', this.selectedTheme);
      formData.append('is_card_note', this.notesOption);

      try {
        const urlip = 'http://localhost:5000/uploadppt'
        const response = await axios.post(urlip, formData, {
          responseType: 'blob',
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log("response",response)
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'generated_ppt.pptx');
        document.body.appendChild(link);
        link.click();

        // Use PptxGenJS to load the PPT and extract the first slide content
        const pptx = new PptxGenJS();
        await pptx.load(blob);
        const firstSlide = pptx.getSlide(0);
        this.pptContent = firstSlide ? firstSlide.text : "无法加载PPT内容";

        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('文件上传失败', error);
        alert('文件上传失败');
      }

      this.showDialog = false; // 关闭主题选择弹窗
    },
    goBack() {
      this.$router.back();
    }
  },
};
</script>
<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.file-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  position: relative;
  font-family: 'Roboto', sans-serif;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.page-title {
  width: 100%;
  text-align: center;
  margin-bottom: 20px;

  h1 {
    font-size: 2.5rem;
    margin: 0;
    color: #333;
    font-weight: 700;
  }
}

.content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  gap: 40px; /* 增加左右部分之间的间距 */
}

.left-section,
.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.upload-section,
.generate-section {
  width: 100%;
  text-align: center;
  margin-bottom: 20px;

  button {
    font-weight: bold;
    font-size: 1em;
    padding: 10px;
    border: 1px solid #007BFF;
    border-radius: 4px;
    cursor: pointer;
    width: 80%;
    max-width: 300px;
    text-align: center;
    background-color: #007BFF;
    color: white;
    border: none;
    transition: background-color 0.3s, transform 0.3s;

    &:hover {
      background-color: #0056b3;
      transform: translateY(-2px);
    }
  }
}

textarea {
  width: 100%;
  height: 500px;
  padding: 10px;
  border: 2px solid #040505; /* 加深边框颜色 */
  border-radius: 4px;
  font-family: inherit;
  resize: none;
  background-color: #fafafa;
  transition: border-color 0.3s;
}

textarea:focus {
  border-color: #040505;
  outline: none;
}

.placeholder-textarea {
  text-align: center;
  font-size: 1.2rem;
  color: #aaa;
  position: relative;
}

.placeholder-textarea::before {
  content: attr(placeholder);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.back-button {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;

  &:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
  }
}

/* Theme Dialog Styles */
.theme-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.theme-dialog-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 600px; /* 调整宽度以容纳更多按钮 */
}

.theme-dialog-content h2 {
  margin-bottom: 20px;
}

.theme-dialog-content h3 {
  margin-bottom: 10px;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.theme-buttons,
.notes-buttons {
  display: flex;
  justify-content: space-around; /* 使按钮在一行中均匀分布 */
  margin-bottom: 10px;
}

.theme-buttons button,
.notes-buttons button {
  flex: 1;
  margin: 0 5px; /* 调整按钮间距 */
  padding: 10px 0; /* 调整按钮高度 */
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;
  text-align: center;

  &.selected {
    background-color: #0056b3;
  }

  &:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
  }
}

.radio-button {
  margin-right: 10px;
}

.radio-button .fa-check-circle {
  color: #007BFF;
}

.radio-button .fa-circle-notch {
  color: #ccc;
}

/* Generate PPT Button */
.generate-ppt-button {
  margin-top: 20px;
  button {
    font-weight: bold;
    font-size: 1em;
    padding: 10px;
    border: 1px solid #007BFF;
    border-radius: 4px;
    cursor: pointer;
    width: 80%;
    max-width: 300px;
    text-align: center;
    background-color: #007BFF;
    color: white;
    border: none;
    transition: background-color 0.3s, transform 0.3s;

    &:hover {
      background-color: #0056b3;
      transform: translateY(-2px);
    }
  }
}
</style>
