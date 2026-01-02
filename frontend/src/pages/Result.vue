<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAlignmentStore } from '../stores/alignment';
import { Activity, CheckCircle2, AlertCircle, ChevronLeft } from 'lucide-vue-next';
import ResultTable from '../components/ResultTable.vue';

const props = defineProps<{
  jobId: string;
}>();

const store = useAlignmentStore();
const router = useRouter();
const pollingInterval = ref<number | null>(null);

const job = computed(() => 
  store.activeJobs.find(j => j.job_id === props.jobId) || null
);

const startPolling = () => {
  if (pollingInterval.value) return;
  
  pollingInterval.value = window.setInterval(async () => {
    try {
      const status = await store.fetchJobStatus(props.jobId);
      if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
        stopPolling();
      }
    } catch (err) {
      stopPolling();
    }
  }, 2000);
};

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
};

onMounted(() => {
  store.fetchJobStatus(props.jobId).then(status => {
    if (status.state !== 'SUCCESS' && status.state !== 'FAILURE') {
      startPolling();
    }
  });
});

onUnmounted(() => {
  stopPolling();
});

const getStatusColor = (state: string) => {
  switch (state) {
    case 'SUCCESS': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
    case 'FAILURE': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
    case 'PENDING': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
    default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
  }
};

const getStatusLabel = (state: string) => {
  switch (state) {
    case 'SUCCESS': return '已完成';
    case 'FAILURE': return '分析失败';
    case 'PENDING': return '正在排队';
    case 'STARTED': return '正在比对';
    default: return state;
  }
};
</script>

<template>
  <div class="animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <button 
        @click="router.push('/')"
        class="flex items-center gap-2 text-slate-400 hover:text-white transition-colors group"
      >
        <ChevronLeft class="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        返回提交页
      </button>
      
      <div v-if="job" :class="['px-4 py-1.5 rounded-full border text-sm font-bold flex items-center gap-2', getStatusColor(job.state)]">
        <Activity v-if="job.state === 'PENDING' || job.state === 'STARTED'" class="w-4 h-4 animate-spin" />
        <CheckCircle2 v-else-if="job.state === 'SUCCESS'" class="w-4 h-4" />
        <AlertCircle v-else class="w-4 h-4" />
        {{ getStatusLabel(job.state) }}
      </div>
    </div>

    <div v-if="job" class="space-y-8">
      <!-- Result Header Card -->
      <div class="bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-2xl overflow-hidden relative">
        <div class="absolute top-0 left-0 w-2 h-full bg-indigo-600" v-if="job.state === 'SUCCESS'"></div>
        <div class="absolute top-0 left-0 w-2 h-full bg-rose-600" v-if="job.state === 'FAILURE'"></div>
        
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 class="text-3xl font-black text-white mb-2 flex items-center gap-3">
              比对分析报告
              <span class="text-slate-600 font-mono text-base font-normal tracking-tight">#{{ job.job_id.slice(0, 12) }}</span>
            </h1>
            <p class="text-slate-400 flex items-center gap-4 text-sm">
              <span v-if="job.result">比对工具: <b class="text-indigo-300 font-bold uppercase">{{ job.result.tool }}</b></span>
              <span v-if="job.result" class="flex items-center gap-1.5">
                命中结果: <b class="text-emerald-400 font-bold">{{ job.result.hits_count }}</b>
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Main Results Table -->
      <div v-if="job.state === 'SUCCESS'" class="space-y-6">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-xl font-bold flex items-center gap-2">
            命中序列详情
            <span class="text-xs font-medium px-2 py-0.5 bg-slate-800 text-slate-400 rounded-md">
              Top 100
            </span>
          </h2>
        </div>
        
        <ResultTable 
          :hits="job.result?.hits || []" 
          :tool="job.result?.tool || 'blast'" 
        />
      </div>

      <!-- Failure State -->
      <div v-else-if="job.state === 'FAILURE'" class="p-16 text-center bg-rose-500/5 border border-rose-500/20 rounded-3xl">
        <div class="w-20 h-20 bg-rose-500/20 text-rose-500 flex items-center justify-center rounded-full mx-auto mb-6">
          <AlertCircle class="w-10 h-10" />
        </div>
        <h3 class="text-2xl font-black text-rose-400 mb-4">比对分析失败</h3>
        <p class="text-slate-400 max-w-lg mx-auto leading-relaxed">
          {{ job.status || '系统在处理您的分析请求时遇到未知错误，请检查输入格式或联系管理员。' }}
        </p>
        <button 
          @click="router.push('/')"
          class="mt-8 px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold transition-all"
        >
          返回重试
        </button>
      </div>

      <!-- Loading State -->
      <div v-else class="p-20 text-center">
        <div class="relative w-24 h-24 mx-auto mb-8">
          <div class="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <div class="absolute inset-4 bg-indigo-600/10 rounded-full flex items-center justify-center">
            <Activity class="w-8 h-8 text-indigo-400 animate-pulse" />
          </div>
        </div>
        <h2 class="text-2xl font-black mb-3">正在执行序列比对...</h2>
        <p class="text-slate-500">大数据量比对可能需要几秒钟，请稍候。</p>
      </div>
    </div>
    
    <div v-else class="p-20 text-center text-slate-500">
       <AlertCircle class="w-12 h-12 mx-auto mb-4 opacity-20" />
       找不到指定的作业 ID 信息。
    </div>
  </div>
</template>
