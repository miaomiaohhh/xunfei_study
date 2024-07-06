// store.js
import { createStore } from 'vuex';

export default createStore({
  state: {
    answers: {
      选择: {},
      填空: {},
      判断: {},
    },
  },
  mutations: {
    saveAnswer(state, { section, questionNumber, answer }) {
      state.answers[section][questionNumber] = answer;
    },
  },
  getters: {
    getAnswer: (state) => (section, questionNumber) => {
      return state.answers[section][questionNumber];
    },
  },
});
