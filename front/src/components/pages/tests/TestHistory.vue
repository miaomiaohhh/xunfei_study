<template>
    <div class="self-test-history">
      <header class="header">
        <h1>自测历史</h1>
        <button class="back-button" @click="goBack">
          <img src="back-icon.svg" alt="Back">
        </button>
      </header>
      <main class="main">
        <div class="scroll-panel">
          <div
            class="history-item"
            v-for="item in history"
            :key="item.id"
            @mouseenter="highlightItem(item.id)"
            @mouseleave="unhighlightItem()"
            @click="goToDetailPage(item.id)"
          >
            <div class="item-info">
              <span class="item-date">{{ item.date }}</span>
              <span class="item-subject">{{ item.subject }}</span>
              <span class="item-topic">{{ item.topic }}</span>
              <span class="item-score">{{ item.score }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        history: [
          { id: 1, date: '2024-07-01', subject: 'Math', topic: 'Algebra', score: '85%' },
          { id: 2, date: '2024-06-25', subject: 'Physics', topic: 'Mechanics', score: '70%' },
          { id: 3, date: '2024-06-18', subject: 'Chemistry', topic: 'Organic Chemistry', score: '92%' },
          // Add more history items as needed
        ],
        highlightedItemId: null,
      };
    },
    methods: {
      goBack() {
        // Implement your back functionality here
        console.log('Navigate back');
      },
      highlightItem(id) {
        this.highlightedItemId = id;
      },
      unhighlightItem() {
        this.highlightedItemId = null;
      },
      goToDetailPage(id) {
        // Implement navigation to detail page here
        console.log(`Navigate to detail page for id ${id}`);
        this.$router.push('/evaluationpage')
      },
    },
  };
  </script>
  
  <style lang="scss">
  .self-test-history {
    font-family: Arial, sans-serif;
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      background-color: #3498db;
      color: #fff;
      h1 {
        font-size: 24px;
        margin: 0;
      }
      .back-button {
        background: none;
        border: none;
        cursor: pointer;
        img {
          width: 24px;
          height: 24px;
        }
      }
    }
    .main {
      padding: 20px;
    }
    .scroll-panel {
      max-height: 400px;
      overflow-y: auto;
      .history-item {
        padding: 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        &:hover {
          background-color: #f0f0f0;
        }
        &:not(:last-child) {
          border-bottom: 1px solid #ccc;
        }
        .item-info {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr 1fr;
          gap: 10px;
          .item-date, .item-subject, .item-topic, .item-score {
            white-space: nowrap; /* Prevent line break */
          }
        }
      }
    }
  }
  </style>
  