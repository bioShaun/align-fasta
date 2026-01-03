<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAlignmentStore } from '../stores/alignment';
import { Search, Activity, Upload, AlertCircle, Settings2 } from 'lucide-vue-next';
import DatabaseSelector from '../components/DatabaseSelector.vue';

const store = useAlignmentStore();
const router = useRouter();

const selectedFile = ref<File | null>(null);
const selectedDbs = ref<string[]>([]);
const selectedTool = ref('blast');
const selectedBlastTask = ref('blastn');
const queryText = ref('');
const inputMethod = ref<'paste' | 'file'>('paste');
const fileInput = ref<HTMLInputElement | null>(null);

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
    <div class="text-center mb-12">
      <h1 class="text-4xl md:text-5xl font-extrabold mb-4 text-gray-900 tracking-tight">
        专业序列比对分析
      </h1>
      <p class="text-gray-500 text-lg max-w-2xl mx-auto font-medium">
        集成 BLAST+ 与 Minimap2 的高性能生物信息学比对服务。
        支持多物种、多基因组版本并行处理。
      </p>
    </div>

    <div class="max-w-5xl mx-auto">
      <div class="bg-white border border-gray-200 p-8 rounded-xl shadow-sm">
        <h2 class="text-xl font-bold mb-8 flex items-center gap-2 text-gray-800">
          <Settings2 class="w-6 h-6 text-primary-600" />
          任务配置中心
        </h2>
        
        <div class="space-y-10">
          <!-- Tool Selection -->
          <section>
            <div class="flex items-center gap-2 mb-4">
              <span class="w-1 h-4 bg-primary-600 rounded-full"></span>
              <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">选择核心工具</label>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button 
                v-for="tool in store.tools" 
                :key="tool.name"
                @click="selectedTool = tool.name"
                :class="[
                  'px-6 py-4 rounded-lg text-sm font-bold border transition-all flex items-center justify-center gap-3',
                  selectedTool === tool.name 
                    ? 'bg-primary-50 border-primary-500 text-primary-700 ring-2 ring-primary-500/20' 
                    : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                ]"
              >
                <Search v-if="tool.name === 'blast'" class="w-4 h-4" />
                <Activity v-else class="w-4 h-4" />
                {{ tool.name.toUpperCase() }}
              </button>
            </div>
          </section>

          <!-- BLAST Task Selection -->
          <section v-if="selectedTool === 'blast'" class="space-y-4 pt-4 border-t border-gray-100">
            <div class="flex items-center gap-2">
              <span class="w-1 h-4 bg-primary-600 rounded-full"></span>
              <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">配置比对模式 (Algorithm Target)</label>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button 
                v-for="task in ['blastn', 'blastn-short', 'megablast', 'dc-megablast']"
                :key="task"
                @click="selectedBlastTask = task"
                :class="[
                  'px-3 py-2.5 rounded-lg text-xs font-bold border transition-all',
                  selectedBlastTask === task
                    ? 'bg-primary-50 border-primary-500 text-primary-700 font-extrabold ring-2 ring-primary-500/20'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ task }}
              </button>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg border border-gray-100">
              <p class="text-[11px] text-gray-500 leading-relaxed italic">
                <span v-if="selectedBlastTask === 'blastn'"><b>blastn</b>: 通用核酸比对，适用于中等相似度序列。</span>
                <span v-else-if="selectedBlastTask === 'blastn-short'"><b>blastn-short</b>: 优化短序列比对 (&lt; 50bp)，如引物或探针。</span>
                <span v-else-if="selectedBlastTask === 'megablast'"><b>megablast</b>: 快速比对高度相似序列 (一致性 &gt; 95%)。</span>
                <span v-else-if="selectedBlastTask === 'dc-megablast'"><b>dc-megablast</b>: 不连续 megablast，适用于远缘同源核酸序列。</span>
              </p>
            </div>
          </section>

          <!-- Database Selection -->
          <section class="pt-4 border-t border-gray-100">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <span class="w-1 h-4 bg-primary-600 rounded-full"></span>
                <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">选择目标数据库</label>
              </div>
              <span v-if="selectedDbs.length > 0" class="text-[11px] text-primary-600 font-bold bg-primary-50 px-2 py-0.5 rounded border border-primary-100">
                已选中 {{ selectedDbs.length }} 个数据库
              </span>
            </div>
            
            <div v-if="store.databases.length > 0">
              <DatabaseSelector 
                :databases="store.databases"
                v-model="selectedDbs"
              />
            </div>
            
            <p v-if="store.databases.length === 0" class="bg-amber-50 border border-amber-200 p-4 rounded-lg text-xs text-amber-700 flex items-center gap-3 mt-3">
              <AlertCircle class="w-5 h-5 flex-shrink-0" /> 
              系统未配置数据库，请联系管理员在 <code>databases.yaml</code> 中添加并完成索引同步。
            </p>
          </section>

          <!-- Query Input -->
          <section class="pt-4 border-t border-gray-100">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <span class="w-1 h-4 bg-primary-600 rounded-full"></span>
                <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">输入查询序列</label>
              </div>
              <!-- Input Method Tabs -->
              <div class="flex gap-1 bg-gray-100 p-1 rounded-lg border border-gray-200">
                <button 
                  @click="inputMethod = 'paste'"
                  :class="[
                    'px-4 py-1.5 text-xs font-bold rounded-md transition-all',
                    inputMethod === 'paste' 
                      ? 'bg-white text-primary-600 shadow-sm' 
                      : 'text-gray-500 hover:text-gray-700'
                  ]"
                >
                  直粘贴
                </button>
                <button 
                  @click="inputMethod = 'file'"
                  :class="[
                    'px-4 py-1.5 text-xs font-bold rounded-md transition-all',
                    inputMethod === 'file' 
                      ? 'bg-white text-primary-600 shadow-sm' 
                      : 'text-gray-500 hover:text-gray-700'
                  ]"
                >
                  文件上传
                </button>
              </div>
            </div>

            <!-- Paste Sequence Textarea -->
            <div v-if="inputMethod === 'paste'" class="relative group">
              <textarea
                v-model="queryText"
                class="w-full bg-gray-50 border border-gray-200 rounded-xl px-5 py-4 text-sm font-mono outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 resize-none h-48 transition-all shadow-inner"
                placeholder=">Sequence_Title
ATGCGATCGTAGCTAGCTAGCTGATCG..."
              ></textarea>
              <div class="mt-2 flex items-center justify-between">
                <p class="text-[11px] text-gray-400 flex items-center gap-2">
                  <Activity class="w-3 h-3 text-primary-500" />
                  支持多条 FASTA 格式序列
                </p>
                <button 
                  @click="queryText = ''" 
                  v-if="queryText"
                  class="text-[11px] text-gray-400 hover:text-red-500 transition-colors"
                >
                  清空内容
                </button>
              </div>
            </div>

            <!-- File Upload -->
            <div v-else>
              <div 
                class="border-2 border-dashed border-gray-200 rounded-xl p-10 text-center hover:border-primary-400 hover:bg-primary-50 transition-all cursor-pointer group"
                @click="fileInput?.click()"
              >
                <input type="file" ref="fileInput" class="hidden" @change="handleFileChange">
                <Upload class="w-10 h-10 text-gray-300 mx-auto mb-3 group-hover:text-primary-500 transition-colors" />
                <p class="text-sm font-bold text-gray-700 mb-1">
                  {{ selectedFile ? selectedFile.name : '点击或拖拽上传 FASTA 文件' }}
                </p>
                <p class="text-xs text-gray-400">支持 .fa, .fasta, .txt (Max 50MB)</p>
              </div>
            </div>
          </section>

          <div class="pt-6">
            <button 
              @click="submitJob"
              :disabled="store.loading || (inputMethod === 'file' && !selectedFile) || (inputMethod === 'paste' && !queryText) || selectedDbs.length === 0"
              class="w-full bg-primary-600 hover:bg-primary-700 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-primary-500/10 disabled:opacity-40 disabled:cursor-not-allowed text-lg active:scale-[0.98]"
            >
              <span v-if="!store.loading" class="flex items-center justify-center gap-2">
                <Search class="w-5 h-5" />
                开启比对任务
              </span>
              <span v-else class="flex items-center justify-center gap-2">
                <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                正在处理数据...
              </span>
            </button>
          </div>
        </div>
      </div>

      <div class="mt-8 flex justify-center pb-12">
        <div class="bg-gray-200/50 backdrop-blur px-5 py-2.5 rounded-full flex items-center gap-4 border border-gray-300/30">
          <div class="flex items-center gap-2 text-xs text-gray-500 font-medium">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            系统状态: 运行中
          </div>
          <div class="w-px h-3 bg-gray-300"></div>
          <p class="text-xs text-gray-400 italic">
            学术引用: AlignFasta Project (2026)
          </p>
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
