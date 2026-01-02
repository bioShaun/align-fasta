<script setup lang="ts">
import ReferenceManager from '../components/ReferenceManager.vue';
import { Database, ChevronLeft } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-5xl mx-auto">
    <div class="flex items-center gap-4 mb-8">
      <button 
        @click="router.push('/')"
        class="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
      >
        <ChevronLeft class="w-6 h-6" />
      </button>
      <div>
        <h1 class="text-3xl font-black text-white flex items-center gap-3">
          <Database class="w-8 h-8 text-indigo-400" />
          数据库管理面板
        </h1>
        <p class="text-slate-500 text-sm mt-1">上传参考基因组并构建 BLAST/Minimap2 索引</p>
      </div>
    </div>

    <div class="bg-slate-900/50 border border-slate-800 p-8 rounded-3xl backdrop-blur-sm shadow-xl">
      <ReferenceManager />
    </div>
  </div>
</template>
