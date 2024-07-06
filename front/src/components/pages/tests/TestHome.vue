<template>
  <div class="online-test">
    <h1>在线测试</h1>

    <div class="block">
      <div class="block-title">科目</div>
      <div class="block-content flex-container">
        <!-- 学科 -->
        <div class="subject-section bordered-container flex-child">
          <div class="section-title">
            学科
            <input
              type="text"
              v-model="subjectSearch"
              class="text-box bordered"
              placeholder="自定义学科"
              @keyup.enter="addCustomSubject"
            />
          </div>
          <div class="button-group">
            <button
              v-for="subject in subjects"
              :key="subject.name"
              @click="openBranchesDialog(subject)"
              :class="{ selected: subject.name === selectedSubject }"
              class="bordered"
            >
              {{ subject.name }}
            </button>
            <!-- 动态渲染用户输入的学科按钮 -->
            <button
              v-if="customSubject"
              @click="openCustomSubjectDialog"
              :class="{ selected: customSubject === selectedSubject }"
              class="bordered"
            >
              {{ customSubject }}
            </button>
          </div>
        </div>
        <!-- 已选 -->
        <div class="selected-section bordered-container flex-child">
    <div class="section-title">
      已选知识点
      <input
        type="text"
        v-model="knowledgeSearch"
        class="text-box bordered"
        placeholder="自定义知识点"
        @keyup.enter="addCustomKnowledge"
      />
    </div>
    <div class="selected-group">
      <div v-if="selectedSubjects.length === 0 && customKnowledges.length === 0" class="placeholder">
        请选择学科知识点
      </div>
      <button v-if="selectedSubjects.length === 0 && customKnowledges.length === 0" class="custom-subject-button" @click="getRecommendedSubjects">
        AI推荐知识点
      </button>
      <div
        v-for="selectedSubject in selectedSubjects"
        :key="selectedSubject"
        class="selected-item"
      >
        {{ selectedSubject }}
        <span
          class="delete-button"
          @click="removeSelectedSubject(selectedSubject)"
        >×</span>
      </div>
      <div
        v-for="knowledge in customKnowledges"
        :key="knowledge"
        class="selected-item"
      >
        {{ knowledge }}
        <span
          class="delete-button"
          @click="removeCustomKnowledge(knowledge)"
        >×</span>
      </div>
      <button v-if="selectedSubjects.length > 0 || customKnowledges.length > 0" class="custom-subject-button" @click="getRecommendedSubjects">
        AI推荐知识点
      </button>
    </div>
  </div>
      </div>
    </div>

    <!-- 弹窗组件 -->
    <div v-if="isBranchesDialogOpen" class="dialog">
      <div class="dialog-content">
        <h2 class="dialog-title"
          >选择学科知识点
          <button class="close-button" @click="closeBranchesDialog">X</button>
        </h2>
        <div class="button-group">
          <button
            v-for="branch in currentBranches"
            :key="branch"
            @click="addToSelected(branch)"
          >
            {{ branch }}
          </button>
        </div>
      </div>
    </div>

    <div class="block">
      <div class="block-title">
        时间(0~120min)
        <input
          type="number"
          v-model.number="timeValue"
          min="0"
          max="120"
          step="5"
          class="input-box"
        />
      </div>
      <div class="block-content">
        <input
          type="range"
          min="0"
          max="120"
          v-model="timeValue"
          class="slider"
          step="5"
        />
      </div>
    </div>

    <div class="block">
      <div class="block-title">
        难度(0~10)
        <input
          type="number"
          v-model.number="difficultyValue"
          min="0"
          max="10"
          step="1"
          class="input-box"
        />
      </div>
      <div class="block-content">
        <input
          type="range"
          min="0"
          max="10"
          v-model="difficultyValue"
          class="slider"
          step="1"
        />
      </div>
    </div>

    <div class="block">
      <div class="block-title">其他要求</div>
      <div class="block-content">
        <textarea class="text-input" v-model="otherInput"></textarea>
      </div>
    </div>

    <button class="start-button" @click="goTestPage">开始测试</button>
    <button class="back-button" @click="goBack">返回</button>
  </div>
  <div v-if="isRecommendedDialogOpen" class="dialog">
      <div class="dialog-content">
        <h2 class="dialog-title">
          推荐知识点
          <button class="close-button" @click="closeRecommendedDialog">关闭</button>
        </h2>
        <div class="recommended-list">
          <div class="recommended-column">
            <label v-for="(subject) in recommendedSubjects" :key="subject" class="recommended-item">
              <input type="checkbox" v-model="selectedRecommendedSubjects" :value="subject">
              {{ subject }}
            </label>
          </div>
        </div>
        <button @click="addSelectedRecommendedSubjects" class="finish-selection-button">完成知识点选择</button>
      </div>
    </div>

    <!-- 加载中弹窗 -->
    <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2>题目生成中...</h2>
      </div>
    </div>
</template>
<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      subjects: [
        {
          name: '数学',
          branches: ['代数', '几何', '微积分', '概率', '统计', '离散数学'],
        },
        {
          name: '计算机',
          branches: ['编程基础', '数据结构', '算法', '操作系统', '数据库', '计算机网络'],
        },
        {
          name: '物理',
          branches: ['力学', '电磁学', '热学', '光学', '量子物理', '相对论'],
        },
        {
          name: '化学',
          branches: ['有机化学', '无机化学', '物理化学', '分析化学', '生物化学', '环境化学'],
        },
        {
          name: '生物',
          branches: ['细胞生物学', '遗传学', '生态学', '进化生物学', '分子生物学', '生物化学'],
        },
        {
          name: '地理',
          branches: ['自然地理', '人文地理', '经济地理', '地质学', '气象学', '环境科学'],
        },
        {
          name: '历史',
          branches: ['中国历史', '世界历史', '古代史', '近现代史', '史学理论', '考古学'],
        },
      ],
      selectedSubjects: [],
      isBranchesDialogOpen: false,
      isRecommendedDialogOpen: false,
      timeValue: 60,
      difficultyValue: 5,
      subjectSearch: '',
      selectedSubjectSearch: '',
      customSubject: '',
      currentBranches: [],
      selectedSubject: '',
      recommendedSubjects: [],
      selectedRecommendedSubjects: [],
      otherInput: '无',
      loading: false,
      isCustomKnowledgeDialogOpen: false,
      knowledgeSearch: '',
      customKnowledge: '',
      customKnowledges: [],
    };
  },
  methods: {
    addCustomKnowledge() {
      if (this.knowledgeSearch && !this.customKnowledges.includes(this.knowledgeSearch)) {
        this.customKnowledges.push(this.knowledgeSearch);
        this.knowledgeSearch = '';
      }
    },
    removeCustomKnowledge(knowledge) {
      this.customKnowledges = this.customKnowledges.filter(k => k !== knowledge);
    },
    addToSelected(branch) {
      if (!this.selectedSubjects.includes(branch)) {
        this.selectedSubjects.push(branch);
      }
    },
    openBranchesDialog(subject) {
      if (this.selectedSubjects.length > 0 && this.selectedSubject !== subject.name) {
        this.selectedSubjects = [];
      }
      this.currentBranches = subject.branches;
      this.isBranchesDialogOpen = true;
      this.selectedSubject = subject.name;
    },
    closeBranchesDialog() {
      this.isBranchesDialogOpen = false;
    },
    goBack() {
      this.$router.back();
    },
    addSelectedSubject() {
      if (this.selectedSubjectSearch && !this.selectedSubjects.includes(this.selectedSubjectSearch)) {
        this.selectedSubjects.push(this.selectedSubjectSearch);
        this.selectedSubjectSearch = '';
      }
    },
    removeSelectedSubject(subject) {
      this.selectedSubjects = this.selectedSubjects.filter((s) => s !== subject);
    },
    addCustomSubject() {
      this.customSubject = this.subjectSearch;
      this.subjectSearch = '';
    },
    closeRecommendedDialog() {
      this.isRecommendedDialogOpen = false;
    },
    async getRecommendedSubjects() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/get_subjects', {
          parent_subjects: [this.selectedSubject],
          already_subjects: this.selectedSubjects,
        });
        this.recommendedSubjects = response.data.subjects;
        this.isRecommendedDialogOpen = true;
      } catch (error) {
        console.error('Error fetching recommended subjects:', error);
      }
    },
    addSelectedRecommendedSubjects() {
      this.selectedSubjects = this.selectedSubjects.concat(this.selectedRecommendedSubjects);
      this.isRecommendedDialogOpen = false;
      this.selectedRecommendedSubjects = [];
    },
    async openCustomSubjectDialog() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/get_subjects', {
          parent_subjects: [this.customSubject],
          already_subjects: this.selectedSubjects,
        });
        this.currentBranches = response.data.subjects;
        this.isBranchesDialogOpen = true;
        this.selectedSubject = this.customSubject;
      } catch (error) {
        console.error('Error fetching custom branches:', error);
      }
    },
    async storeProblems(problems) {
      const db = await openDB('problemsDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('single_choice_problems')) {
            db.createObjectStore('single_choice_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('judgement_problems')) {
            db.createObjectStore('judgement_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('fillin_problems')) {
            db.createObjectStore('fillin_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('evaluation')) {
            console.log("create evaluation")
            db.createObjectStore('evaluation', { keyPath: 'id', autoIncrement: true });
          }
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
            console.log("create suggestion")
            db.createObjectStore('suggestion', { keyPath: 'id', autoIncrement: true });
          }
        },
      });

      // 开始新的事务，先清空所有存储的数据
      const tx = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems'], 'readwrite');
      await Promise.all([
        tx.objectStore('single_choice_problems').clear(),
        tx.objectStore('judgement_problems').clear(),
        tx.objectStore('fillin_problems').clear(),
      ]);
      await tx.done;

      // 重新创建数据库，确保ID从1开始
      const txNew = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems'], 'readwrite');
      let singleChoiceId = 1;
      let judgementId = 1;
      let fillinId = 1;

      problems.forEach((problem) => {
        const problemWithDoneanswer = { ...problem, doneanswer: '' };
        if (problem.type === 'single_choice') {
          txNew.objectStore('single_choice_problems').put({ ...problemWithDoneanswer, id: singleChoiceId++ });
        } else if (problem.type === 'judgement') {
          txNew.objectStore('judgement_problems').put({ ...problemWithDoneanswer, id: judgementId++ });
        } else if (problem.type === 'fillin') {
          txNew.objectStore('fillin_problems').put({ ...problemWithDoneanswer, id: fillinId++ });
        }
      });
      await txNew.done;
    },
    async goTestPage() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:5000/get_problems', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            subjects: this.selectedSubjects,
            time: this.timeValue,
            min_difficulty: 0,
            max_difficulty: this.difficultyValue,
            type: ['single_choice', 'judgement', 'fillin'],
            others: this.otherInput,
          }),
        });
        const data = await response.json();
        await this.storeProblems(data.problems);
      } catch (error) {
        console.error('Error starting test:', error);
      } finally {
        this.loading = false;
        this.$router.push('/testpage');
      }
    },
  },
};
</script>
<style scoped>
.online-test {
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.block {
  margin-bottom: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
}

.block-title {
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.block-content {
  display: flex;
  align-items: center;
}

.subject-section,
.selected-section {
  flex: 1;
  margin-right: 10px;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-weight: bold;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  height: 100%;
  width: 90%;
}

.button-group button {
  position: relative;
  padding-right: 20px; /* 增加右侧内边距给小圆圈留空间 */
}

.button-group button::after {
  content: "";
  position: absolute;
  top: 50%;
  right: 5px; /* 调整圆圈与按钮的距离 */
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid black; /* 设置边框样式 */
  background-color: transparent; /* 设置背景色为透明 */
}

.selected {
  background-color: #28a745; /* Green color when selected */
  color: white; /* White text color when selected */
}

.selected::after {
  background-color: white; /* White color for the circle when selected */
}

.selected-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.selected-item {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.delete-button {
  margin-left: 10px;
  cursor: pointer;
  font-weight: bold;
}

.dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
}

.dialog .dialog-title {
  position: relative;
}

.dialog button.close-button {
  position: absolute;
  top: 1px;
  right: 1px;
  padding: 5px 10px;
  background-color: #ccc;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dialog button {
  margin: 5px;
}

.placeholder {
  padding: 8px 16px;
  background-color: #ffffff;
  border-radius: 4px;
}

.slider {
  width: 100%;
}

.input-box {
  width: 60px;
  margin-left: 10px;
  text-align: center;
}

.text-box {
  width: 50px;
  margin-left: 10px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.text-input {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
}

.start-button {
  display: block;
  margin: 0 auto;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
}

.start-button:hover {
  background-color: #0056b3;
}

.back-button {
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 8px 16px;
  background-color: #ccc;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.bordered {
  border: 1px solid black;
  padding: 5px;
  border-radius: 4px;
}

.bordered-container {
  border: 1px solid black;
  padding: 10px;
  border-radius: 8px;
}

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
}

.loading-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
}

.dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 100%;
}

.dialog-title {
  font-size: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.text-box {
  width: 20%;
  padding: 8px;
  margin-top: 5px;
}

.finish-selection-button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 20px;
}

.flex-container {
  display: flex;
  align-items: stretch;
}

.flex-child {
  flex: 1;
  display: flex;
  flex-direction: column;
}

</style>
