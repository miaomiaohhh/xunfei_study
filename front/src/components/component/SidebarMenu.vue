<template>
  <div class="sidebar-menu">
    <div class="app-title">智慧书苑</div>
    <ul>
      <li @click="toggleMenu('home')">首页</li>
      
      <!-- 教师应用 -->
      <li>
        <div @click="toggleMenu('teacherApplication')">教师应用</div>
        <ul v-if="isActiveMenu('teacherApplication')" class="submenu">
          <li @click="navigate('/pptgenerator')">PPT生成</li>
          <li @click="navigate('/homeworkmanagement')">作业管理</li>
          <li @click="navigate('/teacherrecording')">教师录课</li>
          <li @click="navigate('/classselect')">课程观看</li>
        </ul>
      </li>

      <!-- 学生应用 -->
      <li>
        <div @click="toggleMenu('studentApplication')">学生应用</div>
        <ul v-if="isActiveMenu('studentApplication')" class="submenu">
          <li @click="navigate('/virtualperson')">虚拟人</li>
          <li @click="navigate('/educationalconsulting')">教育咨询</li>
          <li @click="navigate('/testhome')">开始测试</li>
          <li @click="navigate('/evaluationpage')">测试历史</li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeMenus: ['teacherApplication', 'studentApplication'], // 初始展开的菜单项
    };
  },
  methods: {
    navigate(route) {
      this.$router.push(route);
    },
    toggleMenu(menu) {
      if (this.isActiveMenu(menu)) {
        this.activeMenus = this.activeMenus.filter(item => item !== menu); // Close the menu if it's already open
      } else {
        this.activeMenus.push(menu); // Open the clicked menu
      }
    },
    isActiveMenu(menu) {
      return this.activeMenus.includes(menu);
    },
  },
};
</script>

<style scoped lang="scss">
.sidebar-menu {
  width: 200px;
  background-color: #1a8dec;
  color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  font-family: 'Arial, sans-serif';

  .app-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
    color: #fff;
  }

  ul {
    list-style-type: none;
    padding: 0;

    li {
      padding: 10px 15px;
      margin: 5px 0;
      cursor: pointer;
      background-color: #2a9df4;
      border-radius: 5px;
      transition: background-color 0.3s, color 0.3s, transform 0.3s;
      position: relative;

      &:hover {
        background-color: #0056b3;
        color: #fff;
        transform: translateY(-2px);
      }

      .submenu {
        margin-top: 10px;

        li {
          background-color: #4fa3f7;
          border-radius: 5px;

          &:hover {
            background-color: #0056b3;
          }
        }
      }
    }
  }
}
</style>
