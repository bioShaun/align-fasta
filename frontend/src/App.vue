<script setup lang="ts">
import { Activity } from 'lucide-vue-next';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const navItems = [] as { name: string, path: string, icon: any }[];
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-primary-500/10">
    <!-- Navbar -->
    <nav class="border-b border-gray-200 bg-white/80 backdrop-blur-xl sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-24">
          <div 
            class="flex items-center gap-3 cursor-pointer group" 
            @click="router.push('/')"
          >
            <!-- GenoScope Logo Image Only -->
            <img src="/logo-new-size.png" alt="GenoScope Logo" class="h-20 w-auto object-contain" />
          </div>

          <!-- Desktop Nav -->
          <div class="hidden md:flex items-center gap-8 text-sm font-medium">
            <template v-for="item in navItems" :key="item.path">
              <a 
                href="#"
                @click.prevent="router.push(item.path)"
                :class="[
                  'flex items-center gap-2 transition-all px-3 py-2 rounded-md',
                  route.path === item.path 
                    ? 'text-primary-600 bg-primary-50' 
                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                ]"
              >
                <component :is="item.icon" class="w-4 h-4" />
                {{ item.name }}
              </a>
            </template>
            
            <div v-if="navItems.length > 0" class="h-4 w-px bg-gray-200 mx-2"></div>
            
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
    <footer class="border-t border-gray-200 mt-24 py-12 text-gray-500 text-sm bg-white">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-2">
            <Activity class="w-4 h-4 text-primary-600" />
            <span class="font-bold text-gray-800">AlignFasta</span>
          </div>
          <p>© 2026 AlignFasta 专业序列比对服务。基于 FastAPI, Vue 3 和 Celery 构建。</p>
          <div class="flex gap-6">
            <a href="#" class="hover:text-primary-600 transition-colors">联系支持</a>
            <a href="#" class="hover:text-primary-600 transition-colors">API 文档</a>
            <a href="#" class="hover:text-primary-600 transition-colors">隐私权政策</a>
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
  @apply bg-gray-50;
}
::-webkit-scrollbar-thumb {
  @apply bg-gray-200 rounded-full border-4 border-gray-50 hover:bg-gray-300;
}

/* Typography polish */
body {
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}
</style>
