<script setup lang="ts">
import { Activity, Search, Database, History, HelpCircle } from 'lucide-vue-next';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const navItems = [
  { name: '序列比对', path: '/', icon: Search },
  { name: '管理面板', path: '/admin', icon: Database },
  { name: '比对历史', path: '/history', icon: History },
];
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">
    <!-- Navbar -->
    <nav class="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div 
            class="flex items-center gap-3 cursor-pointer group" 
            @click="router.push('/')"
          >
            <div class="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
              <Activity class="w-6 h-6 text-white" />
            </div>
            <span class="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
              AlignFasta
            </span>
          </div>

          <!-- Desktop Nav -->
          <div class="hidden md:flex items-center gap-8 text-sm font-bold">
            <template v-for="item in navItems" :key="item.path">
              <a 
                href="#"
                @click.prevent="router.push(item.path)"
                :class="[
                  'flex items-center gap-2 transition-all px-3 py-2 rounded-lg',
                  route.path === item.path 
                    ? 'text-white bg-white/5' 
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                ]"
              >
                <component :is="item.icon" class="w-4 h-4" />
                {{ item.name }}
              </a>
            </template>
            
            <div class="h-4 w-px bg-slate-800 mx-2"></div>
            
            <a href="#" class="text-slate-500 hover:text-white transition-colors">
              <HelpCircle class="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <router-view v-slot="{ Component }">
        <transition 
          enter-active-class="transform transition ease-out duration-300"
          enter-from-class="opacity-0 translate-y-4"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transform transition ease-in duration-200"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-4"
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800 mt-24 py-12 text-slate-500 text-sm">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-2">
            <Activity class="w-4 h-4 text-indigo-500" />
            <span class="font-bold text-slate-400">AlignFasta</span>
          </div>
          <p>© 2026 AlignFasta 专业序列比对服务。基于 FastAPI, Vue 3 和 Celery 构建。</p>
          <div class="flex gap-6">
            <a href="#" class="hover:text-white transition-colors">联系支持</a>
            <a href="#" class="hover:text-white transition-colors">API 文档</a>
            <a href="#" class="hover:text-white transition-colors">隐私权政策</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* Global smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Custom scrollbars */
::-webkit-scrollbar {
  width: 10px;
}
::-webkit-scrollbar-track {
  @apply bg-slate-950;
}
::-webkit-scrollbar-thumb {
  @apply bg-slate-800 rounded-full border-4 border-slate-950 hover:bg-slate-700;
}

/* Typography polish */
body {
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}
</style>
