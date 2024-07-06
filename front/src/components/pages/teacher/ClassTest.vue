<template>
    <div class="test-page">
      <header>
        <span class="title">测试</span>
        <button class="return-button" @click="returnToPreviousPage">返回</button>
      </header>
      <main>
        <aside class="sidebar">
          <div class="timer-container">
            <div class="time">考试时间：{{ formattedMinutes }}:{{ formattedSeconds }}</div>
            <button @click="submitTest" class="submit-button">交卷</button>
          </div>
          <div class="section" v-for="section in sections" :key="section.name">
            <div class="section-title">{{ section.name }}</div>
            <div class="question-status-container">
              <div
                class="question-status"
                v-for="question in section.questions"
                :key="question.id"
                :class="{ 'done': isQuestionDone(section.name, question.id), 'not-done': !isQuestionDone(section.name, question.id) }"
                @click="jumpToQuestion(section.name, question.id)"
              >
                {{ question.id }}
              </div>
            </div>
          </div>
        </aside>
        <div class="content">
          <h2>{{ currentSection ? currentSection.name : '' }} 题 第{{ currentQuestionIndex + 1 }}题</h2>
          <div v-if="currentQuestion" :key="currentQuestion.id">
            <div v-if="currentSection && currentSection.name === '选择'" class="choice-question">
              <div class="question-content">{{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}</div>
              <div class="options">
                <div v-for="(option, index) in currentQuestion.choices" :key="index" class="option" @click="selectOption(index)">
                  <span>{{ index }}. {{ option }}</span>
                  <span class="circle" :class="{ selected: this.selectedOption === index }"></span>
                </div>
              </div>
            </div>
            <div v-if="currentSection && currentSection.name === '填空'" class="fill-blank-question">
              <div class="question-content">{{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}</div>
              <input type="text" class="input-box" placeholder="请输入答案" v-model="filledAnswer" />
            </div>
            <div v-if="currentSection && currentSection.name === '判断'" class="judge-question">
              <div class="question-content">{{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}</div>
              <div class="options">
                <div class="option" @click="selectOption(true)">
                  <span>正确</span>
                  <span class="circle" :class="{ selected: selectedOption === true }"></span>
                </div>
                <div class="option" @click="selectOption(false)">
                  <span>错误</span>
                  <span class="circle" :class="{ selected: selectedOption === false }"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="buttons">
            <div class="navigation-buttons">
              <button @click="previousQuestion">上一题</button>
              <button @click="nextQuestion">下一题</button>
            </div>
          </div>
        </div>
      </main>
      <!-- AI正在阅卷中...弹窗 -->
      <div v-if="grading" class="grading-dialog">
        <div class="grading-content">
          <h2>AI正在阅卷中...</h2>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { openDB } from 'idb';
  import axios from 'axios';
  
  export default {
    data() {
      return {
        timer: null,
        minutes: 0,
        seconds: 0,
        sections: [
          { name: '选择', questions: [], done: [], answers: {} },
          { name: '填空', questions: [], done: [], answers: {} },
          { name: '判断', questions: [], done: [], answers: {} }
        ],
        currentSection: null,
        currentQuestionIndex: 0,
        selectedOption: null,
        filledAnswer: '',
        questionContents: {},
        grading: false // 新增属性，控制“AI正在阅卷中...”弹窗显示
      };
    },
    computed: {
      formattedMinutes() {
        return this.minutes.toString().padStart(2, '0');
      },
      formattedSeconds() {
        return this.seconds.toString().padStart(2, '0');
      },
      currentQuestion() {
        if (this.currentSection && this.currentSection.questions) {
          return this.currentSection.questions[this.currentQuestionIndex];
        }
        return null;
      },
      currentQuestionContent() {
        if (this.currentQuestion) {
          return this.currentQuestion.problem;
        }
        return '';
      }
    },
    methods: {
      async loadQuestions() {
        try {
          const db = await openDB('ClassTestProblems', 1);
          await this.loadQuestionsByType(db, 'fillin', '填空');
          await this.loadQuestionsByType(db, 'judgement', '判断');
          await this.loadQuestionsByType(db, 'single_choice', '选择');
          this.currentSection = this.sections[0];
        } catch (error) {
          console.error('Failed to load questions:', error);
        }
      },
      async loadQuestionsByType(db, tableName, type) {
        const questions = await db.getAll(tableName);
        const section = this.sections.find(sec => sec.name === type);
        if (section) {
          section.questions.push(...questions);
        }
      },
      startTimer() {
        this.timer = setInterval(() => {
          this.seconds++;
          if (this.seconds === 60) {
            this.minutes++;
            this.seconds = 0;
          }
        }, 1000);
      },
      returnToPreviousPage() {
        this.$router.back();
      },
      jumpToQuestion(sectionName, questionId) {
        if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
          this.saveCurrentAnswer();
        }
        const section = this.sections.find(sec => sec.name === sectionName);
        if (section) {
          this.currentSection = section;
          this.currentQuestionIndex = section.questions.findIndex(q => q.id === questionId);
          this.restoreAnswer();
        } else {
          console.error('Section not found:', sectionName);
        }
      },
      saveCurrentAnswer() {
        if (!this.currentSection) return;
  
        const answer = this.currentSection.name === '选择' || this.currentSection.name === '判断'
          ? this.selectedOption
          : this.filledAnswer;
  
        this.currentSection.answers[this.currentQuestionIndex] = answer;
  
        if (!this.currentSection.done.includes(this.currentQuestionIndex)) {
          this.currentSection.done.push(this.currentQuestionIndex);
        }
      },
      restoreAnswer() {
        if (!this.currentSection) return;
  
        const answer = this.currentSection.answers[this.currentQuestionIndex];
        this.filledAnswer = ''; // Clear the filledAnswer by default
        this.selectedOption = null; // Clear the selectedOption by default
        if (answer !== undefined) {
          if (this.currentSection.name === '选择' || this.currentSection.name === '判断') {
            this.selectedOption = answer;
          } else if (this.currentSection.name === '填空') {
            this.filledAnswer = answer;
          }
        }
      },
      isQuestionDone(sectionName, questionId) {
        const section = this.sections.find(sec => sec.name === sectionName);
        if (section) {
          const questionIndex = section.questions.findIndex(q => q.id === questionId);
          return section.done.includes(questionIndex);
        }
        return false;
      },
      selectOption(option) {
        this.selectedOption = option;
        this.saveCurrentAnswer();
      },
      nextQuestion() {
        if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
          this.saveCurrentAnswer();
        }
        if (this.currentSection && this.currentQuestionIndex < this.currentSection.questions.length - 1) {
          this.currentQuestionIndex++;
        } else {
          const currentSectionIndex = this.sections.indexOf(this.currentSection);
          if (currentSectionIndex < this.sections.length - 1) {
            this.currentSection = this.sections[currentSectionIndex + 1];
            this.currentQuestionIndex = 0;
          }
        }
        this.restoreAnswer();
      },
      previousQuestion() {
        if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
          this.saveCurrentAnswer();
        }
        if (this.currentQuestionIndex > 0) {
          this.currentQuestionIndex--;
        } else {
          const currentSectionIndex = this.sections.indexOf(this.currentSection);
          if (currentSectionIndex > 0) {
            this.currentSection = this.sections[currentSectionIndex - 1];
            this.currentQuestionIndex = this.currentSection.questions.length - 1;
          }
        }
        this.restoreAnswer();
      },
      async getIndexedDBData() {
        const db = await openDB('ClassTestProblems', 1);
        const data = {
          single_choice_problems: await db.getAll('single_choice_problems'),
          fillin_problems: await db.getAll('fillin_problems'),
          judgement_problems: await db.getAll('judgement_problems')
        };
        return data;
      },
      async saveResponseToIndexedDB(responseData) {
        try {
          const db = await openDB('ClassTestProblems', 1);
          for (const [tableName, problems] of Object.entries(responseData)) {
            console.log('tableName',tableName)
            for (const problem of problems) {
              await db.put(tableName, problem);
            }
          }
        } catch (error) {
          console.error('Failed to save response to IndexedDB:', error);
        }
      },
      async submitTest() {
        this.grading = true; // 显示“AI正在阅卷中...”弹窗
  
        async function clearTable(db, tableName) {
          const tx = db.transaction(tableName, 'readwrite');
          const store = tx.objectStore(tableName);
          await store.clear();
          await tx.done;
        }
  
        try {
          const db = await openDB('ClassTestProblems', 1);
          for (const section of this.sections) {
            const tableName = this.getTableName(section.name);
            for (const question of section.questions) {
              const answer = section.answers[question.id - 1]; // Adjust index if necessary
              if (answer !== undefined) {
                const updatedQuestion = JSON.parse(JSON.stringify({ ...question, doneanswer: answer }));
                await db.put(tableName, updatedQuestion);
              }
            }
          }
          const useranswer = await this.getIndexedDBData();
          const response = await axios.post('http://localhost:5000/submit_test', useranswer);
          console.log('response.data', response.data);
  
          const tableNames = ['evaluation', 'dimension', 'score', 'shortcoming', 'suggestion'];
          for (const tableName of tableNames) {
            await clearTable(db, tableName);
          }
  
          const transaction = db.transaction(tableNames, 'readwrite');
          for (const [key, value] of Object.entries(response.data)) {
            if (key === 'knowledge_radar') {
              const store_dimension = transaction.objectStore('dimension');
              await Promise.all(value.dimension.map((dim, index) => store_dimension.put({ id: index + 1, dimension: dim })));
              const store_score = transaction.objectStore('score');
              await Promise.all(value.score.map((sc, index) => store_score.put({ id: index + 1, score: sc })));
            } else {
              const store = transaction.objectStore(key);
              await store.put({ id: 1, content: value });
            }
          }
          await transaction.done;
          alert('测试已提交');
          this.$router.push('/classtestevaluation');
        } catch (error) {
          console.error('Failed to submit test:', error);
        } finally {
          this.grading = false; // 隐藏“AI正在阅卷中...”弹窗
        }
      },
      getTableName(sectionName) {
        switch (sectionName) {
          case '选择':
            return 'single_choice_problems';
          case '填空':
            return 'fillin_problems';
          case '判断':
            return 'judgement_problems';
          default:
            throw new Error('Unknown section name: ' + sectionName);
        }
      }
    },
    async mounted() {
      await this.loadQuestions();
      this.startTimer();
      this.restoreAnswer();
    },
    beforeUnmount() {
      clearInterval(this.timer);
    }
  };
  </script>
  
  <style lang="scss" scoped>
  .test-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
  
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px;
      background-color: #f8f8f8;
      border-bottom: 1px solid #ddd;
  
      .title {
        flex: 1;
        text-align: center;
        font-size: 2em;
        font-weight: bolder;
      }
  
      .return-button {
        padding: 10px 10px;
        font-size: 1em;
        cursor: pointer;
        background-color: #1d8ade;
        color: #fff;
        border: none;
        border-radius: 5px;
      }
    }
  
    main {
      display: flex;
      flex: 1;
  
      .sidebar {
        width: 20%;
        padding: 20px;
        background-color: #f0f0f0;
        border-right: 1px solid #ddd;
        overflow-y: auto;
  
        .section-title {
          font-weight: bold;
          margin-bottom: 10px;
        }
  
        .question-status-container {
          display: flex;
          flex-wrap: wrap;
        }
  
        .question-status {
          margin: 5px;
          padding: 5px;
          cursor: pointer;
          border: 1px solid #ccc;
          background-color: #fff;
          width: 30px;
          height: 30px;
          text-align: center;
          line-height: 30px;
  
          &.done {
            background-color: green;
            color: white;
          }
  
          &.not-done {
            background-color: rgb(157, 154, 154);
            color: white;
          }
        }
      }
  
      .content {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
  
        h2 {
          font-size: 1.5em;
          margin-bottom: 20px;
        }
  
        .question-content {
          font-size: 1.2em;
          margin-bottom: 10px;
        }
  
        .options {
          display: flex;
          flex-direction: column;
  
          .option {
            display: flex;
            align-items: center;
            cursor: pointer;
            margin-bottom: 5px;
  
            .circle {
              width: 20px;
              height: 20px;
              border: 1px solid #ccc;
              border-radius: 50%;
              margin-right: 10px;
            }
  
            .circle.selected {
              background-color: #1d8ade;
              border: 1px solid #168cac;
            }
          }
        }
  
        .input-box {
          width: 100%;
          height: 40px;
          padding: 5px;
          font-size: 1em;
          border: 1px solid #ccc;
          border-radius: 5px;
          margin-bottom: 10px;
        }
  
        .buttons {
          margin-top: 20px;
  
          .navigation-buttons {
            display: flex;
            justify-content: space-between;
          }
  
          button {
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            background-color: #1d8ade;
            color: #fff;
            border: none;
            border-radius: 5px;
          }
        }
      }
    }
  }
  
  .grading-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
  
    .grading-content {
      background-color: #fff;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
    }
  }
  </style>
  