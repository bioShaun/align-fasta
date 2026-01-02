<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAlignmentStore } from '../stores/alignment';
import { Search, Activity, Upload, AlertCircle, CheckCircle2 } from 'lucide-vue-next';
import type { Database } from '../types';

const store = useAlignmentStore();
const router = useRouter();

const selectedFile = ref<File | null>(null);
const selectedDbs = ref<string[]>([]);
const selectedTool = ref('blast');
const selectedBlastTask = ref('blastn');
const queryText = ref('');
const inputMethod = ref<'paste' | 'file'>('paste');
const fileInput = ref<HTMLInputElement | null>(null);

// 按物种分组的数据库
const groupedDatabases = computed(() => {
  const groups: Record<string, Database[]> = {};
  store.databases.forEach(db => {
    const species = db.species || '未分类物种';
    if (!groups[species]) groups[species] = [];
    groups[species].push(db);
  });
  return groups;
});

watch(queryText, (newVal) => {
  const sequences = newVal.split(/^>/m).filter(Boolean);
  let maxSeqLen = 0;
  for (const seq of sequences) {
    const lines = seq.split('\n').slice(1);
    const seqLen = lines.join('').replace(/\s/g, '').length;
    maxSeqLen = Math.max(maxSeqLen, seqLen);
  }
  if (maxSeqLen > 0 && maxSeqLen < 50) {
    selectedBlastTask.value = 'blastn-short';
  } else if (selectedBlastTask.value === 'blastn-short') {
    selectedBlastTask.value = 'blastn';
  }
});

onMounted(() => {
  store.fetchDatabases();
  store.fetchTools();
});

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0] || null;
  }
};

const toggleDb = (dbId: string) => {
  const index = selectedDbs.value.indexOf(dbId);
  if (index === -1) {
    selectedDbs.value.push(dbId);
  } else {
    selectedDbs.value.splice(index, 1);
  }
};

const submitJob = async () => {
  if (selectedDbs.value.length === 0) return;

  try {
    let input: File | string | null = null;
    if (inputMethod.value === 'file') {
      if (!selectedFile.value) return;
      input = selectedFile.value;
    } else {
      if (!queryText.value) return;
      input = queryText.value;
    }

    if (!input) return;

    const options: any = {};
    if (selectedTool.value === 'blast') {
      options.task = selectedBlastTask.value;
    }

    const job = await store.submitAlignment(input, selectedDbs.value, selectedTool.value, options);
    
    if (job) {
      router.push({ name: 'result', params: { jobId: job.job_id } });
    }
  } catch (err) {
    console.error(err);
  }
};
</script>

<template>
  <div class="animate-in fade-in duration-500">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <h1 class="text-4xl md:text-6xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-400">
        序列比对服务
      </h1>
      <p class="text-slate-400 text-lg max-w-2xl mx-auto">
        使用 BLAST+ 和 Minimap2 快速比对序列。
        支持跨物种、多数据库并行分析。
      </p>
    </div>

    <div class="max-w-4xl mx-auto">
      <div class="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl backdrop-blur-sm shadow-xl">
        <h2 class="text-xl font-semibold mb-8 flex items-center gap-2">
          <Search class="w-6 h-6 text-indigo-400" />
          比对配置
        </h2>
        
        <div class="space-y-8">
          <!-- Tool Selection -->
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-3">选择比对工具</label>
            <div class="grid grid-cols-2 gap-4">
              <button 
                v-for="tool in store.tools" 
                :key="tool.name"
                @click="selectedTool = tool.name"
                :class="[
                  'px-6 py-3 rounded-xl text-sm font-bold border transition-all duration-200',
                  selectedTool === tool.name 
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/20 scale-[1.02]' 
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                ]"
              >
                {{ tool.name.toUpperCase() }}
              </button>
            </div>
          </div>

          <!-- BLAST Task Selection -->
          <div v-if="selectedTool === 'blast'" class="space-y-3">
            <label class="block text-sm font-medium text-slate-400">选择比对模式 (Task)</label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button 
                v-for="task in ['blastn', 'blastn-short', 'megablast', 'dc-megablast']"
                :key="task"
                @click="selectedBlastTask = task"
                :class="[
                  'px-3 py-2 rounded-lg text-xs font-bold border transition-all',
                  selectedBlastTask === task
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg'
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                ]"
              >
                {{ task }}
              </button>
            </div>
            <p class="text-[10px] text-slate-500 leading-relaxed italic border-l-2 border-indigo-500/30 pl-3">
              <span v-if="selectedBlastTask === 'blastn'"><b>blastn</b>: 通用核酸比对，适用于中等相似度序列。</span>
              <span v-else-if="selectedBlastTask === 'blastn-short'"><b>blastn-short</b>: 优化短序列比对 (&lt; 50bp)，如引物或探针。</span>
              <span v-else-if="selectedBlastTask === 'megablast'"><b>megablast</b>: 快速比对高度相似序列 (一致性 &gt; 95%)。</span>
              <span v-else-if="selectedBlastTask === 'dc-megablast'"><b>dc-megablast</b>: 不连续 megablast，适用于远缘同源核酸序列。</span>
            </p>
          </div>

          <!-- Database Selection -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-medium text-slate-400">选择目标数据库 (可多选)</label>
              <span class="text-[10px] text-indigo-400 font-bold uppercase tracking-wider px-2 py-0.5 bg-indigo-500/10 rounded">
                已选: {{ selectedDbs.length }}
              </span>
            </div>
            
            <div v-if="store.databases.length > 0" class="space-y-4 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
              <div v-for="(dbs, species) in groupedDatabases" :key="species" class="space-y-2">
                <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">{{ species }}</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div 
                    v-for="db in dbs" 
                    :key="db.id"
                    @click="toggleDb(db.id)"
                    :class="[
                      'p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between group',
                      selectedDbs.includes(db.id)
                        ? 'bg-indigo-600/20 border-indigo-500/50 text-white'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600'
                    ]"
                  >
                    <div class="flex flex-col">
                      <span class="text-sm font-bold">{{ db.name }}</span>
                      <div class="flex gap-1 mt-1">
                        <span v-if="db.sequence_type" class="text-[9px] px-1 bg-slate-700 text-slate-300 rounded uppercase">
                          {{ db.sequence_type }}
                        </span>
                        <span v-if="db.genome_version" class="text-[9px] px-1 bg-slate-700 text-slate-300 rounded">
                          {{ db.genome_version }}
                        </span>
                      </div>
                    </div>
                    <CheckCircle2 
                      :class="[
                        'w-5 h-5 transition-all',
                        selectedDbs.includes(db.id) ? 'text-indigo-400 scale-110' : 'text-slate-700 group-hover:text-slate-500'
                      ]" 
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <p v-if="store.databases.length === 0" class="text-xs text-amber-400 mt-3 flex items-center gap-2">
              <AlertCircle class="w-4 h-4" /> 未找到数据库。请在管理面板上传。
            </p>
          </div>

          <!-- Query Input -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-medium text-slate-400">查询序列</label>
              <!-- Input Method Tabs -->
              <div class="flex gap-1 bg-slate-800 p-1 rounded-lg border border-slate-700">
                <button 
                  @click="inputMethod = 'paste'"
                  :class="[
                    'px-3 py-1 text-xs font-bold rounded-md transition-all',
                    inputMethod === 'paste' 
                      ? 'bg-indigo-600 text-white shadow-sm' 
                      : 'text-slate-500 hover:text-slate-300'
                  ]"
                >
                  粘贴文本
                </button>
                <button 
                  @click="inputMethod = 'file'"
                  :class="[
                    'px-3 py-1 text-xs font-bold rounded-md transition-all',
                    inputMethod === 'file' 
                      ? 'bg-indigo-600 text-white shadow-sm' 
                      : 'text-slate-500 hover:text-slate-300'
                  ]"
                >
                  上传文件
                </button>
              </div>
            </div>

            <!-- Paste Sequence Textarea -->
            <div v-if="inputMethod === 'paste'" class="relative group">
              <textarea
                v-model="queryText"
                class="w-full bg-slate-800 border border-slate-700 rounded-2xl px-5 py-4 text-sm font-mono outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none h-48 transition-all group-hover:border-slate-600 shadow-inner"
                placeholder=">序列名称
ATGCGATCGTAGCTAGCTAGCTGATCG..."
              ></textarea>
              <p class="text-xs text-slate-500 mt-2 flex items-center gap-2">
                <Activity class="w-3 h-3 text-indigo-400" />
                在上方粘贴您的 FASTA 格式序列
              </p>
            </div>

            <!-- File Upload -->
            <div v-else>
              <div 
                class="border-2 border-dashed border-slate-700 rounded-2xl p-12 text-center hover:border-indigo-500 hover:bg-indigo-500/5 transition-all cursor-pointer group"
                @click="fileInput?.click()"
              >
                <input type="file" ref="fileInput" class="hidden" @change="handleFileChange">
                <Upload class="w-12 h-12 text-slate-600 mx-auto mb-4 group-hover:text-indigo-400 group-hover:scale-110 transition-all" />
                <p class="text-sm font-medium text-slate-300 mb-1">
                  {{ selectedFile ? selectedFile.name : '点击上传或拖拽文件到这里' }}
                </p>
                <p class="text-xs text-slate-500">支持 .fa, .fasta 类型文件</p>
              </div>
            </div>
          </div>

          <button 
            @click="submitJob"
            :disabled="store.loading || (inputMethod === 'file' && !selectedFile) || (inputMethod === 'paste' && !queryText) || selectedDbs.length === 0"
            class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed text-lg tracking-wider"
          >
            {{ store.loading ? '正在处理...' : '开始比对分析' }}
          </button>
        </div>
      </div>

      <div class="mt-8 flex justify-center">
        <div class="bg-indigo-600/10 border border-indigo-500/20 px-6 py-3 rounded-full flex items-center gap-4">
          <div class="flex items-center gap-2 text-xs text-slate-400">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            工作节点: 在线
          </div>
          <div class="w-px h-3 bg-slate-700"></div>
          <div class="flex items-center gap-2 text-xs text-slate-400">
            <Activity class="w-3 h-3 text-indigo-400" />
            队列长度: 正常
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
