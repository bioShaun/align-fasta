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
    case 'SUCCESS': return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    case 'FAILURE': return 'text-rose-600 bg-rose-50 border-rose-200';
    case 'PENDING': return 'text-amber-600 bg-amber-50 border-amber-200';
    default: return 'text-gray-500 bg-gray-50 border-gray-200';
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
        class="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors group text-sm font-medium"
      >
        <ChevronLeft class="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        返回搜索界面
      </button>
      
      <div v-if="job" :class="['px-4 py-1.5 rounded-md border text-xs font-bold flex items-center gap-2', getStatusColor(job.state)]">
        <Activity v-if="job.state === 'PENDING' || job.state === 'STARTED'" class="w-3.5 h-3.5 animate-spin" />
        <CheckCircle2 v-else-if="job.state === 'SUCCESS'" class="w-3.5 h-3.5" />
        <AlertCircle v-else class="w-3.5 h-3.5" />
        {{ getStatusLabel(job.state) }}
      </div>
    </div>

    <div v-if="job" class="space-y-8">
      <!-- Result Header Card -->
      <div class="bg-white border border-gray-200 p-8 rounded-xl shadow-sm overflow-hidden relative">
        <div class="absolute top-0 left-0 w-1.5 h-full bg-primary-600" v-if="job.state === 'SUCCESS'"></div>
        <div class="absolute top-0 left-0 w-1.5 h-full bg-rose-500" v-if="job.state === 'FAILURE'"></div>
        
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
              序列比对分析报告
              <span class="text-gray-400 font-mono text-sm font-normal tracking-tight">ID: {{ job.job_id.slice(0, 12) }}</span>
            </h1>
            <div class="flex items-center gap-6 mt-3 text-sm">
              <span v-if="job.result" class="flex items-center gap-1.5 text-gray-600">
                比对工具: <b class="text-gray-900 font-bold uppercase">{{ job.result.tool }}</b>
              </span>
              <span v-if="job.result" class="flex items-center gap-1.5 text-gray-600">
                命中结果: <b class="text-primary-600 font-bold">{{ job.result.hits_count }}</b>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Results Table -->
      <div v-if="job.state === 'SUCCESS'" class="space-y-6">
        <div class="flex items-center justify-between px-2">
          <h2 class="text-lg font-bold flex items-center gap-2 text-gray-800">
            比对命中详情
            <span class="text-[10px] font-bold px-2 py-0.5 bg-gray-100 text-gray-500 rounded border border-gray-200 uppercase tracking-tighter">
              Summary Mode
            </span>
          </h2>
        </div>
        
        <ResultTable 
          :hits="job.result?.hits || []" 
          :tool="job.result?.tool || 'blast'" 
        />
      </div>

      <!-- Failure State -->
      <div v-else-if="job.state === 'FAILURE'" class="p-16 text-center bg-white border border-rose-200 rounded-xl shadow-sm">
        <div class="w-16 h-16 bg-rose-50 text-rose-500 flex items-center justify-center rounded-full mx-auto mb-6 border border-rose-100">
          <AlertCircle class="w-8 h-8" />
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-3">任务分析中断</h3>
        <p class="text-gray-500 max-w-lg mx-auto text-sm leading-relaxed">
          {{ job.status || '系统在处理您的分析请求时遇到未知错误，请检查输入格式或联系管理员。' }}
        </p>
        <button 
          @click="router.push('/')"
          class="mt-8 px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-bold transition-all shadow-md shadow-primary-500/10"
        >
          返回重试
        </button>
      </div>

      <!-- Loading State -->
      <div v-else class="p-20 text-center bg-white border border-gray-100 rounded-xl shadow-sm">
        <div class="relative w-20 h-20 mx-auto mb-8">
          <div class="absolute inset-0 border-4 border-primary-100 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-3">比对计算中...</h2>
        <p class="text-gray-500 text-sm">BLAST/Minimap2 引擎正在扫描目标库，这通常需要几秒钟。</p>
      </div>
    </div>
    
    <div v-else class="p-20 text-center text-gray-400 bg-white border border-gray-100 rounded-xl">
       <AlertCircle class="w-10 h-10 mx-auto mb-4 opacity-20" />
       <p class="text-sm italic">未找到作业 ID #{{ jobId }}</p>
    </div>
  </div>
</template>
