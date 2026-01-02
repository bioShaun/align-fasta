import { createRouter, createWebHashHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import Result from '../pages/Result.vue';

const routes = [
    { path: '/', name: 'home', component: Home },
    { path: '/result/:jobId', name: 'result', component: Result, props: true },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

export default router;
