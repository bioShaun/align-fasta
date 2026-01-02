<script setup lang="ts">
import { History } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto text-center py-20">
    <div class="w-24 h-24 bg-slate-900 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-slate-800 shadow-xl">
       <History class="w-12 h-12 text-slate-600" />
    </div>
    <h1 class="text-4xl font-black mb-4 text-white">历史记录</h1>
    <p class="text-slate-500 max-w-lg mx-auto mb-10 leading-relaxed">
       本地历史记录功能正在开发中。目前您可以点击顶部的 AlignFasta 返回首页进行新的比对工作。
    </p>
    <button 
      @click="router.push('/')"
      class="px-10 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-black shadow-xl shadow-indigo-600/20 transition-all"
    >
      立即开始比对
    </button>
  </div>
</template>
