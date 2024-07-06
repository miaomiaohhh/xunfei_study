import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../components/pages/login/LoginPage.vue';
import IndexPage from '../components/pages/index/IndexPage.vue';
import PPTGeneratorPage from '@/components/pages/teacher/PPTGeneratorPage.vue';
import HomeworkManagement from '@/components/pages/teacher/HomeworkManagement.vue';
import TestHome from '@/components/pages/tests/TestHome.vue';
import TestPage from '@/components/pages/tests/TestPage.vue';
import EvaluationPage from '@/components/pages/tests/EvaluationPage.vue';
import TestAnswer from '@/components/pages/tests/TestAnswer.vue';
import TestHistory from '@/components/pages/tests/TestHistory.vue';
import HexagonChart from '@/components/component/HexagonChart.vue';
import SidebarMenu from '@/components/component/SidebarMenu.vue';
import AiQa from '@/components/pages/aiqa/AiQa.vue';
import VirtualTeacher from '@/components/pages/aiqa/VirtualTeacher.vue';
import TeacherRecording from '@/components/pages/classrecord/TeacherRecording.vue';
import ClassSelect from '@/components/pages/classrecord/ClassSelect.vue'
import ClassStudy from '@/components/pages/classrecord/ClassStudy.vue'
import CourseHelper from '@/components/pages/teacher/CourseHelper.vue';
import ClassTest from '@/components/pages/teacher/ClassTest.vue'
import ClassTestEvaluation from '@/components/pages/teacher/ClassTestEvaluation.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/index',
    name: 'Index',
    component: IndexPage,
  },
  {
    path: '/pptgenerator',
    name: 'PPTGenerator',
    component: PPTGeneratorPage,
  },
  {
    path: '/testhome',
    name: 'TestHome',
    component: TestHome,
  },
  {
    path: '/testpage',
    name: 'TestPage',
    component: TestPage,
  },
  {
    path: '/testhistory',
    name: 'TestHistory',
    component: TestHistory,
  },
  {
    path: '/testanswer',
    name: 'TestAnswer',
    component: TestAnswer,
  },
  {
    path: '/evaluationpage',
    name: 'EvaluationPage',
    component: EvaluationPage,
  },
  {
    path: '/hexagonchart',
    name: 'HexagonChart',
    component: HexagonChart,
  },
  {
    path: '/homeworkmanagement',
    name: 'HomeworkManagement',
    component: HomeworkManagement,
  },
  {
    path: '/sidebarmenu',
    name: 'SidebarMenu',
    component: SidebarMenu,
  },
  {
    path: '/aiqa',
    name: 'AiQa',
    component: AiQa,
  },
  {
    path: '/virtualteacher',
    name: 'VirtualTeacher',
    component: VirtualTeacher,
  },
  {
    path: '/teacherrecording',
    name: 'TeacherRecording',
    component: TeacherRecording,
  },
  {
    path: '/classselect',
    name: 'ClassSelect',
    component: ClassSelect,
  },
  {
    path: '/classstudy',
    name: 'ClassStudy',
    component: ClassStudy,
  },
  {
    path: '/coursehelper',
    name: 'CourseHelper',
    component: CourseHelper,
  },
  {
    path: '/classtest',
    name: 'ClassTest',
    component: ClassTest,
  },
  {
    path: '/classtestevaluation',
    name: 'ClassTestEvaluation',
    component: ClassTestEvaluation,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
