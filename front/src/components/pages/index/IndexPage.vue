<template>
  <div class="home">
    <!-- Sidebar Menu -->
    <SidebarMenu />

    <div class="main-content">
      <!-- Page Title -->
      <div class="page-title">
        <h1>智慧书苑</h1>
      </div>

      <!-- Application Switch Tabs -->
      <div class="switch-tabs">
        <div class="tab" :class="{ active: activeTab === 'teacher' }" @click="switchTab('teacher')">教师应用</div>
        <div class="tab" :class="{ active: activeTab === 'student' }" @click="switchTab('student')">学生应用</div>
      </div>

      <!-- Teacher Application Section -->
      <div v-if="activeTab === 'teacher'">
        <!-- Top Section: Teacher Assistant -->
        <div class="top-section">
          <h2 class="section-title">教师助手</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/coursehelper')">
              <h3 class="button-title">课程记录</h3>
              <p class="button-description">记录教师的课程信息，方便管理和回顾。</p>
            </div>
            <div class="button" @click="handleClick('/homeworkmanagement')">
              <h3 class="button-title">背诵批改</h3>
              <p class="button-description">管理学生的背诵作业，包括布置、查看和反馈。</p>
            </div>
            <div class="button" @click="handleClick('/pptgenerator')">
              <h3 class="button-title">PPT生成</h3>
              <p class="button-description">创建和编辑教学用的幻灯片，简化制作过程。</p>
            </div>
          </div>
        </div>

        <!-- Middle Section: Intelligent Q&A -->
        <div class="middle-section">
          <h2 class="section-title">智能问答</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/virtualteacher')">
              <h3 class="button-title">虚拟人</h3>
              <p class="button-description">与虚拟人进行互动，获取实时帮助。</p>
            </div>
            <div class="button" @click="handleClick('/aiqa')">
              <h3 class="button-title">教育咨询</h3>
              <p class="button-description">获取教育相关的咨询和建议。</p>
            </div>
          </div>
        </div>

        <!-- Course Management Section -->
        <div class="course-management-section">
          <h2 class="section-title">课程管理</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/teacherrecording')">
              <h3 class="button-title">教师录课</h3>
              <p class="button-description">录制教师的课程内容。</p>
            </div>
            <div class="button" @click="handleClick('/classselect')">
              <h3 class="button-title">课程观看</h3>
              <p class="button-description">观看录制好的课程。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Application Section -->
      <div v-if="activeTab === 'student'">
        <!-- Bottom Section: Online Testing -->
        <div class="bottom-section">
          <h2 class="section-title">在线测试</h2>
          <div class="button-container">
            <button class="button" @click="startTest" title="进入选择不同测试">
              <h3 class="button-title">开始测试</h3>
              <p class="button-description">选择不同的测试方式以开始测试。</p>
            </button>
            <button class="button" @click="viewHistory" title="回顾最近的测试情况">
              <h3 class="button-title">测试历史</h3>
              <p class="button-description">查看最近的测试情况和结果。</p>
            </button>
          </div>
        </div>
        <!-- Middle Section: Intelligent Q&A -->
        <div class="middle-section">
          <h2 class="section-title">智能问答</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/virtualteacher')">
              <h3 class="button-title">虚拟人</h3>
              <p class="button-description">与虚拟人进行互动，获取实时帮助。</p>
            </div>
            <div class="button" @click="handleClick('/aiqa')">
              <h3 class="button-title">教育咨询</h3>
              <p class="button-description">获取教育相关的咨询和建议。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="top-right">
        <button class="logout-button" @click="logout">
          <i class="fas fa-arrow-left"></i><span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import SidebarMenu from '../../component/SidebarMenu.vue';

export default {
  name: 'TeacherManagement',
  components: {
    SidebarMenu
  },
  data() {
    return {
      activeTab: 'teacher' // 默认显示教师应用内容
    };
  },
  methods: {
    handleClick(buttonroute) {
      this.$router.push(buttonroute);
      console.log(`go to ${buttonroute}`);
    },
    startTest() {
      this.$router.push('/testhome');
    },
    viewHistory() {
      this.$router.push('/testhistory');
    },
    logout() {
      this.$router.back();
    },
    switchTab(tab) {
      this.activeTab = tab;
    }
  }
};
</script>

<style scoped lang="scss">
/* Styles for Home Component */
.home {
  display: flex;
  position: relative;
  text-align: center;
  padding: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  color: #333;
  font-family: 'Arial, sans-serif';

  .main-content {
    flex: 1;
    margin-left: 20px; /* Adjust this value based on the sidebar width */
  }

  .page-title {
    margin-top: 5px;
    margin-bottom: 20px;

    h1 {
      font-size: 2.5rem;
      color: #333;
      margin: 0;
    }
  }

  .switch-tabs {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 20px;

    .tab {
      padding: 10px 20px;
      font-size: 1.2rem;
      cursor: pointer;
      border-radius: 5px;
      background-color: #1a8dec;
      color: #fff;
      transition: background-color 0.3s, color 0.3s;

      &:hover {
        background-color: #584eec;
      }

      &.active {
        background-color: #584eec;
      }
    }
  }

  .top-section,
  .middle-section,
  .bottom-section,
  .course-management-section {
    margin-bottom: 20px;
    padding: 20px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
  }

  .section-title {
    font-size: 2rem;
    margin-bottom: 20px;
    margin-top: 3px;
    color: #555;
  }

  .button-container {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .button {
    flex: 1;
    padding: 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s, color 0.3s, transform 0.3s;
    background: #1a8dec;
    color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

    &:hover {
      background: #584eec;
      transform: translateY(-5px);
    }

    h3 {
      font-size: 1.4rem;
      margin-bottom: 10px;
    }

    p {
      font-size: 1rem;
      margin-top: 10px;
    }
  }

  .top-right {
    position: absolute;
    top: 30px;
    right: 20px;
  }

  .logout-button {
    display: flex;
    align-items: center; /* 垂直居中图标和文本 */
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
      margin-right: 8px; /* 增加图标和文本之间的间距 */
    }

    span {
      margin-left: 8px;
    }
  }
}
</style>
