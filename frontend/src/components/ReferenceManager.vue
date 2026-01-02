<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useAlignmentStore } from '../stores/alignment';
import type { Database } from '../types';
import { Database as DatabaseIcon, Trash2, Zap, Upload, CheckCircle2, AlertCircle, Edit3, Save, X } from 'lucide-vue-next';

const store = useAlignmentStore();
const showUpload = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

// 编辑状态管理
const editingDbId = ref<string | null>(null);
const editForm = reactive({
  species: '',
  genome_version: '',
  sequence_type: '',
  description: ''
});

const sequenceTypes = [
  { value: 'genome', label: '基因组 (Genome)' },
  { value: 'cds', label: '编码序列 (CDS)' },
  { value: 'protein', label: '蛋白质 (Protein)' },
  { value: 'transcript', label: '转录本 (Transcript)' }
];

const handleUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    if (file) {
      await store.uploadReference(file);
      showUpload.value = false;
    }
  }
};

const deleteDb = async (id: string) => {
  if (confirm(`确定要删除数据库 ${id} 吗？相关索引也将被移除。`)) {
    await store.deleteDatabase(id);
  }
};

const createIndex = async (id: string, tool: string) => {
  await store.createIndex(id, tool);
};

const startEdit = (db: Database) => {
  editingDbId.value = db.id;
  editForm.species = db.species || '';
  editForm.genome_version = db.genome_version || '';
  editForm.sequence_type = db.sequence_type || '';
  editForm.description = db.description || '';
};

const cancelEdit = () => {
  editingDbId.value = null;
};

const saveEdit = async (dbId: string) => {
  await store.updateDatabase(dbId, {
    species: editForm.species || undefined,
    genome_version: editForm.genome_version || undefined,
    sequence_type: editForm.sequence_type || undefined,
    description: editForm.description || undefined
  });
  editingDbId.value = null;
};
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <DatabaseIcon class="w-6 h-6 text-indigo-400" />
        参考数据库列表
      </h2>
      <button 
        @click="showUpload = !showUpload"
        class="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-black transition-all shadow-lg shadow-indigo-600/20"
      >
        <Upload class="w-4 h-4" />
        上传 FASTA 参考序列
      </button>
    </div>

    <!-- Upload Panel -->
    <div v-if="showUpload" class="bg-indigo-600/5 border-2 border-dashed border-indigo-500/30 rounded-2xl p-8 animate-in fade-in slide-in-from-top-4 duration-300">
      <input type="file" ref="fileInput" class="hidden" @change="handleUpload" accept=".fa,.fasta">
      <div 
        @click="fileInput?.click()"
        class="flex flex-col items-center justify-center p-12 border-2 border-dashed border-slate-700 hover:border-indigo-500 hover:bg-indigo-500/5 rounded-xl cursor-pointer transition-all group"
      >
        <Upload class="w-12 h-12 text-slate-600 mb-4 group-hover:text-indigo-400 group-hover:scale-110 transition-all" />
        <p class="text-base font-bold text-slate-300">点击或将 FASTA 文件拖拽至此</p>
        <p class="text-xs text-slate-500 mt-2">支持扩展名: .fa, .fasta</p>
      </div>
    </div>

    <!-- Database List -->
    <div class="grid grid-cols-1 gap-6">
      <div v-if="store.databases.length === 0" class="text-center py-20 bg-slate-900/50 border border-slate-800 rounded-3xl border-dashed">
        <DatabaseIcon class="w-16 h-16 text-slate-800 mx-auto mb-4" />
        <p class="text-slate-500 text-lg">暂无参考数据库，请先上传。</p>
      </div>

      <div 
        v-for="db in store.databases" 
        :key="db.id"
        class="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl hover:border-indigo-500/30 transition-all group relative overflow-hidden shadow-lg"
      >
        <div class="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
           <DatabaseIcon class="w-32 h-32" />
        </div>
        
        <div class="flex items-start justify-between relative z-10">
          <div class="flex items-start gap-5 flex-1">
            <div class="p-4 bg-slate-800 rounded-2xl shadow-inner group-hover:bg-indigo-600/10 transition-colors">
              <DatabaseIcon class="w-8 h-8 text-indigo-400" />
            </div>
            <div class="flex-1">
              <h3 class="text-xl font-black text-slate-100">{{ db.name }}</h3>
              <p class="text-xs text-slate-500 font-mono mt-2 flex items-center gap-2">
                <span class="px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">路径</span>
                {{ db.path }}
              </p>
              
              <!-- 元数据显示/编辑 -->
              <div v-if="editingDbId !== db.id" class="mt-4 space-y-2">
                <div v-if="db.species || db.genome_version || db.sequence_type" class="flex flex-wrap gap-2">
                  <span v-if="db.species" class="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-lg border border-emerald-500/20">
                    🧬 {{ db.species }}
                  </span>
                  <span v-if="db.genome_version" class="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-lg border border-blue-500/20">
                    📌 {{ db.genome_version }}
                  </span>
                  <span v-if="db.sequence_type" class="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs rounded-lg border border-purple-500/20">
                    📄 {{ db.sequence_type.toUpperCase() }}
                  </span>
                </div>
                <p v-if="db.description" class="text-xs text-slate-400 italic">{{ db.description }}</p>
                <p v-if="!db.species && !db.genome_version && !db.sequence_type && !db.description" class="text-xs text-slate-600">
                  未配置元数据，点击编辑按钮添加
                </p>
              </div>
              
              <!-- 编辑表单 -->
              <div v-else class="mt-4 space-y-3 bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="text-xs text-slate-500 block mb-1">物种名称</label>
                    <input 
                      v-model="editForm.species"
                      type="text"
                      placeholder="如：Oryza sativa"
                      class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500/50 outline-none"
                    >
                  </div>
                  <div>
                    <label class="text-xs text-slate-500 block mb-1">基因组版本</label>
                    <input 
                      v-model="editForm.genome_version"
                      type="text"
                      placeholder="如：IRGSP-1.0"
                      class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500/50 outline-none"
                    >
                  </div>
                </div>
                <div>
                  <label class="text-xs text-slate-500 block mb-1">序列类型</label>
                  <select 
                    v-model="editForm.sequence_type"
                    class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500/50 outline-none"
                  >
                    <option value="">请选择...</option>
                    <option v-for="st in sequenceTypes" :key="st.value" :value="st.value">
                      {{ st.label }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="text-xs text-slate-500 block mb-1">描述信息</label>
                  <input 
                    v-model="editForm.description"
                    type="text"
                    placeholder="数据库描述..."
                    class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500/50 outline-none"
                  >
                </div>
                <div class="flex gap-2 justify-end">
                  <button 
                    @click="cancelEdit"
                    class="px-3 py-1.5 text-slate-400 hover:text-white text-sm flex items-center gap-1"
                  >
                    <X class="w-4 h-4" /> 取消
                  </button>
                  <button 
                    @click="saveEdit(db.id)"
                    class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-bold flex items-center gap-1"
                  >
                    <Save class="w-4 h-4" /> 保存
                  </button>
                </div>
              </div>
              
              <div class="flex gap-3 mt-6">
                <div 
                  v-for="tool in ['blast', 'minimap2']" 
                  :key="tool"
                  :class="[
                    'px-3 py-1.5 rounded-xl text-[10px] uppercase font-black tracking-widest flex items-center gap-2 border transition-all',
                    db.tools.includes(tool) 
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                      : 'bg-slate-800/50 text-slate-600 border-slate-800'
                  ]"
                >
                  <CheckCircle2 v-if="db.tools.includes(tool)" class="w-3.5 h-3.5" />
                  <AlertCircle v-else class="w-3.5 h-3.5" />
                  {{ tool }} 索引
                </div>
              </div>
            </div>
          </div>

          <div class="flex gap-2 flex-col">
            <!-- 编辑按钮 -->
            <button 
              v-if="editingDbId !== db.id"
              @click="startEdit(db)"
              class="p-3 text-slate-500 hover:text-indigo-400 hover:bg-indigo-400/10 rounded-2xl transition-all border border-transparent hover:border-indigo-400/20"
              title="编辑元数据"
            >
              <Edit3 class="w-5 h-5" />
            </button>
            
            <div class="flex flex-col gap-2">
              <button 
                v-if="!db.tools.includes('blast')"
                @click="createIndex(db.id, 'blast')"
                class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-black shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-2"
              >
                <Zap class="w-3.5 h-3.5" />
                构建 BLAST 索引
              </button>
              <button 
                v-if="!db.tools.includes('minimap2')"
                @click="createIndex(db.id, 'minimap2')"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-black shadow-lg shadow-purple-600/20 transition-all flex items-center gap-2"
              >
                <Zap class="w-3.5 h-3.5" />
                构建 MM2 索引
              </button>
            </div>
            
            <button 
              @click="deleteDb(db.id)"
              class="p-3 text-slate-500 hover:text-rose-400 hover:bg-rose-400/10 rounded-2xl transition-all border border-transparent hover:border-rose-400/20"
              title="删除数据库"
            >
              <Trash2 class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
