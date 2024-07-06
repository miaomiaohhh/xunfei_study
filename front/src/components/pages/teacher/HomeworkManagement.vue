<template>
  <div class="homework-management">
    <!-- Page Title -->
    <div class="page-title">
      <h1>背诵管理</h1>
    </div>

    <!-- Return Button -->
    <div class="top-right">
      <button class="return-button" @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
    </div>

    <!-- Content Section -->
    <div class="content">
      <!-- Left Section -->
      <div class="left-section">
        <div class="upload-container">
          <!-- Upload Answer Button -->
          <button class="upload-answer-button" @click="triggerAnswerUpload"><i class="fas fa-file-upload"></i> 上传答案</button>
          <!-- File Input for Answer Upload -->
          <input type="file" id="answer-upload" ref="answerUpload" style="display: none" @change="handleAnswerUpload">
          
          <!-- File Upload Button for Homework -->
          <input type="file" id="file-upload" ref="fileUpload" multiple style="display: none" @change="handleFileUpload">
          <button class="upload-button" @click="triggerFileUpload"><i class="fas fa-upload"></i> {{ uploadButtonText }}</button>
        </div>

        <!-- Standard Answer Title -->
        <h2 class="standard-answer-title">标准答案</h2>
        <!-- Standard Answer Textarea -->
        <textarea class="standard-answer" v-model="standardAnswer" placeholder="标准答案"></textarea>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <h2>批改结果</h2>
        <div class="upload-info">
          <div class="info-item">
            <span>上传作业数量：</span>
            <div class="info-value">{{ uploadResults.length }}</div>
          </div>
          <div class="info-item">
            <span>平均正确率：</span>
            <div class="info-value">{{ calculateAccuracy() }}%</div>
          </div>
        </div>
        <div class="upload-results">
          <table>
            <thead>
              <tr>
                <th>序号</th>
                <th>文件名</th>
                <th>正确率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in uploadResults" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ result.filename }}</td>
                <td>{{ result.accuracy }}</td>
              </tr>
              <tr v-for="index in emptyRows" :key="'empty' + index">
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeworkManagement',
  data() {
    return {
      standardAnswer: '',
      uploadResults: [],
      uploadButtonText: '批量上传作业',
      initialRows: 15
    };
  },
  computed: {
    emptyRows() {
      return Math.max(this.initialRows - this.uploadResults.length, 0);
    }
  },
  methods: {
    triggerFileUpload() {
      this.$refs.fileUpload.click();
    },
    handleFileUpload(event) {
      const files = event.target.files;

      const formData = new FormData();

      //const int file_count = files.length;
      formData.append("num_files",files.length);
      // 将文本框中的答案字符串转换为 txt 文件
      const standardAnswerFile = new File([this.standardAnswer], 'standardanswer.txt', {
        type: 'text/plain'
      });

      // 将标准答案文件添加到 FormData 对象中
      formData.append('answer', standardAnswerFile);

      // 将作业文件添加到 FormData 对象中
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formData.append('audio_files', file);
      }

      // 发送给后端
      // const url = 'http://127.0.0.1:5000/uploadhomework';
      const url = 'http://10.10.228.190:5000/uploadhomework';
      
      console.log('formData',formData)
      fetch(url, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        // 处理后端返回的 accuracy_results
        console.log('accuracy_results:', data);
        this.uploadResults.push(...Object.entries(data).map(([filename, accuracy]) => ({ filename, accuracy })));
        console.log(this.uploadResults)
        this.uploadButtonText = '继续上传作业';
      })
      .catch(error => {
        console.error('Error:', error);
      });
    },
    triggerAnswerUpload() {
      this.$refs.answerUpload.click();
    },
    handleAnswerUpload(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.standardAnswer = e.target.result;
      };
      reader.readAsText(file);
    },
    calculateAccuracy() {
      if (this.uploadResults.length === 0) return 0;

      const totalAccuracy = this.uploadResults.reduce((total, result) => {
        let accuracy = result.accuracy;
        // 使用正则表达式提取数值部分
        const match = accuracy.match(/([\d.]+)/);
        if (match) {
          accuracy = parseFloat(match[1]);
        } else {
          accuracy = NaN;
        }

        if (!isNaN(accuracy)) {
          return total + accuracy;
        } else {
          console.warn(`Invalid accuracy value: ${result.accuracy}`);
          return total;
        }
      }, 0);

      const averageAccuracy = totalAccuracy / this.uploadResults.length;
      return averageAccuracy.toFixed(2);
    },
    goBack() {
      this.$router.go(-1); // 返回到上一页
    }
  }
};
</script>

<style scoped lang="scss">
.homework-management {
  text-align: center;
  padding: 10px;
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  color: #333;
  font-family: 'Arial, sans-serif';
  position: relative;

  .page-title {
    margin-bottom: 20px;

    h1 {
      font-size: 2.5rem;
      color: #333;
      margin: 0;
    }
  }

  .top-right {
    position: absolute;
    top: 20px;
    right: 20px;
  }

  .return-button {
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
    background: #3778e0;
    color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

    &:hover {
      background: #584eec;
      transform: translateY(-5px);
    }
  }

  .content {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-top: 20px;
    height: 85vh;

    .left-section,
    .right-section {
      flex-grow: 1;
      background: #ffffff;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .left-section {
      display: flex;
      flex-direction: column;
      align-items: center;

      .upload-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px; /* 缩小间距 */
      }

      .upload-answer-button,
      .upload-button {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px 20px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.3s;
        background: #3778e0;
        color: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

        &:hover {
          background: #584eec;
          transform: translateY(-5px);
        }

        i {
          margin-right: 5px;
        }
      }

      .upload-button {
        margin-left: 10px;
      }

      .standard-answer-title {
        font-size: 1.5rem;
        color: #444;
        text-align: center;
        margin-bottom: 10px; /* 缩小间距 */
      }

      .standard-answer {
        width: 100%;
        height: 100%;
        margin-bottom: 20px;
        padding: 10px;
        border: 1px solid #0f0e0e;
        border-radius: 5px;
        font-size: 1rem;
        resize: none;
      }
    }

    .right-section {
      display: flex;
      flex-direction: column;
      align-items: center;

      h2 {
        font-size: 1.5rem;
        color: #444;
        margin-bottom: 10px;
      }

      .upload-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 10px;

        .info-item {
          font-weight: bold;
          display: flex;
          align-items: center;
          margin-right: 30px;
        }

        .info-value {
          padding: 5px;
          margin-left: 5px;
        }
      }

      .upload-results {
        overflow-y: auto;
        height: 74%;
        width: 100%;
        border: 2px solid #000;
        border-radius: 3px;
        padding: 10px;

        table {
          width: 100%;
          border-collapse: collapse;

          th, td {
            border: 1px solid #797777;
            padding: 8px;
            text-align: center;
          }

          th {
            background-color: #f2f2f2;
          }

          tr:hover {
            background-color: #e6f7ff;
          }
        }
      }
    }

    /* 移除右侧部分的悬停效果 */
    .right-section:hover {
      transform: none;
      box-shadow: none;
    }
  }
}
</style>
