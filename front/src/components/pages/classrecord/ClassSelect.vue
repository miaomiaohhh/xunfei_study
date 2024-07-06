<template>
  <div class="course-selection" @click="hideDropdown">
    <header class="header">
      <h1>学生选课</h1>
      <div class="tabs">
        <div
          v-for="tab in tabs"
          :key="tab"
          :class="['tab', { active: tab === selectedTab }]"
          @click="selectTab(tab)"
        >
          {{ tab }}
        </div>
        <div
          class="tab"
          @mouseenter="showMoreMenu"
          @mouseleave="hideMoreMenu"
        >
          更多
          <div class="more-menu" v-if="isMoreMenuVisible" @click.stop>
            <div class="more-items">
              <div v-for="(item, index) in moreTabs" :key="index" class="more-item" @click="selectTab(item)">
                {{ item }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="search-and-back">
        <input type="text" placeholder="搜索课程" v-model="searchQuery" @input="filterCourses" />
        <button class="back-button" @click="goBack">返回</button>
      </div>
    </header>
    <div class="course-list">
      <div v-for="course in paginatedCourses" :key="course.id" class="course-item">
        <h2>{{ course.name }}</h2>
        <p>{{ course.description }}</p>
        <button @click="selectCourse(course)">学习</button>
      </div>
    </div>
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
      <span>第 {{ currentPage }} 页</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '',
      selectedTab: '数学',
      tabs: ['数学', '英语', '计算机', '化学', '物理', '历史'],
      moreTabs: ['文学', '医学', '生物'],
      courses: [
        { id: 1, name: '数学课程1', description: '数学课程描述1' },
        { id: 2, name: '物理课程1', description: '物理课程描述1' },
        { id: 3, name: '化学课程1', description: '化学课程描述1' },
        { id: 4, name: '数学课程2', description: '数学课程描述2' },
        { id: 5, name: '物理课程2', description: '物理课程描述2' },
        { id: 6, name: '化学课程2', description: '化学课程描述2' },
        { id: 7, name: '数学课程3', description: '数学课程描述3' },
        { id: 8, name: '物理课程3', description: '物理课程描述3' },
        { id: 9, name: '化学课程3', description: '化学课程描述3' },
        { id: 10, name: '医学课程1', description: '医学课程描述1' },
        // 添加更多课程
      ],
      filteredCourses: [],
      isMoreMenuVisible: false,
      currentPage: 1,
      itemsPerPage: 6,
    };
  },
  computed: {
    paginatedCourses() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredCourses.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredCourses.length / this.itemsPerPage);
    }
  },
  mounted() {
    this.filterCourses();
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    filterCourses() {
      const searchRegex = new RegExp(this.searchQuery, 'i'); // 模糊搜索正则表达式，不区分大小写
      this.filteredCourses = this.courses.filter(course =>
        searchRegex.test(course.name) && course.name.includes(this.selectedTab)
      );
      this.currentPage = 1;
    },
    selectCourse(course) {
      console.log(course.name);
      // alert(`你已选择课程: ${course.name}`);
      this.$router.push('/classstudy');
    },
    selectTab(tab) {
      if (tab !== '更多') {
        this.selectedTab = tab;
        this.filterCourses();
      }
    },
    showMoreMenu() {
      this.isMoreMenuVisible = true;
    },
    hideMoreMenu() {
      this.isMoreMenuVisible = false;
    },
    handleClickOutside(event) {
      if (this.$el && !this.$el.contains(event.target)) {
        this.hideMoreMenu();
      }
    },
    hideDropdown() {
      this.isMoreMenuVisible = false;
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>

<style lang="scss">
.course-selection {
  padding: 20px;
  font-family: Arial, sans-serif;
  position: relative; /* To ensure the pagination absolute positioning is relative to this container */
  min-height: 92vh; /* Ensure the container takes full height */

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h1 {
      margin: 0;
    }

    .tabs {
      display: flex;
      gap: 10px;
      position: relative;

      .tab {
        padding: 10px 20px;
        background-color: #1a8dec;
        color: #fff;
        border-radius: 5px;
        cursor: pointer;
        position: relative;

        &.active {
          background-color: #584eec;
        }

        &:hover {
          background-color: #3399ff;
        }

        .more-menu {
          position: absolute;
          top: 100%;
          left: 0;
          display: grid;
          grid-template-columns: repeat(3, 1fr); // 每行显示3个按钮项
          background-color: #1199e2;
          border: 1px solid #ddd;
          border-radius: 5px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          padding: 10px;
          z-index: 1000;
          width: auto; // 自动调整宽度

          .more-items {
            width: 100%;
            display: grid;
            grid-template-columns: repeat(3, 1fr); // 每行显示3个按钮项

            .more-item {
              padding: 10px;
              cursor: pointer;
              display: flex;
              align-items: center; // 垂直居中
              justify-content: center; // 水平居中
              white-space: nowrap; // 保持单行显示
              &:hover {
                background-color: #2317c4;
              }
            }
          }
        }
      }
    }

    .search-and-back {
      display: flex;
      gap: 10px;

      input {
        padding: 5px;
        font-size: 16px;
      }

      .back-button {
        padding: 5px 10px;
        background-color: #1a8dec;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;

        &:hover {
          background-color: #584eec;
        }
      }
    }
  }

  .course-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;

    .course-item {
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 5px;
      background-color: #f9f9f9;
      text-align: center;

      h2 {
        margin-top: 0;
      }

      p {
        font-size: 14px;
        color: #666;
      }

      button {
        padding: 10px 20px;
        background-color: #1a8dec;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;

        &:hover {
          background-color: #584eec;
        }
      }
    }
  }

  .pagination {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;

    button {
      padding: 5px 10px;
      background-color: #1a8dec;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;

      &:disabled {
        background-color: #ddd;
        cursor: not-allowed;
      }
    }
  }
}
</style>
