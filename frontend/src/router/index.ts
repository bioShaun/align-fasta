import { createRouter, createWebHashHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import Result from '../pages/Result.vue';
import Admin from '../pages/Admin.vue';
import History from '../pages/History.vue';

const routes = [
    { path: '/', name: 'home', component: Home },
    { path: '/result/:jobId', name: 'result', component: Result, props: true },
    { path: '/admin', name: 'admin', component: Admin },
    { path: '/history', name: 'history', component: History },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

export default router;
