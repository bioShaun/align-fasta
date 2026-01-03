<script setup lang="ts">
import { ref, computed } from 'vue';
import { Search, CheckCircle2, Circle, XCircle } from 'lucide-vue-next';
import type { Database } from '../types';

const props = defineProps<{
  databases: Database[];
  modelValue: string[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void;
}>();

const searchQuery = ref('');
const selectedSpecies = ref<string | null>(null);

// sequence_type 本地化映射与排序权重
const typeLabelMap: Record<string, { label: string; order: number }> = {
  genome: { label: '基因组', order: 1 },
  cds: { label: 'CDS', order: 2 },
  exon: { label: '外显子', order: 3 },
};

// 获取类型的显示名称
const getTypeLabel = (type: string): string => {
  return typeLabelMap[type]?.label || type.charAt(0).toUpperCase() + type.slice(1);
};

// 获取类型的排序权重
const getTypeOrder = (type: string): number => {
  return typeLabelMap[type]?.order || 999;
};

// 按物种分组数据库
const groupedDatabases = computed(() => {
  const groups: Record<string, Database[]> = {};
  props.databases.forEach(db => {
    const species = db.species || 'Unclassified';
    if (!groups[species]) groups[species] = [];
    groups[species].push(db);
  });
  return groups;
});

// 过滤后的物种列表
const filteredSpecies = computed(() => {
  const speciesList = Object.keys(groupedDatabases.value).sort();
  if (!searchQuery.value) return speciesList;
  
  const query = searchQuery.value.toLowerCase();
  return speciesList.filter(s => s.toLowerCase().includes(query));
});

// 计算统计信息
const statsPerSpecies = computed(() => {
  const stats: Record<string, { total: number; selected: number }> = {};
  Object.entries(groupedDatabases.value).forEach(([species, dbs]) => {
    const total = dbs.length;
    const selected = dbs.filter(db => props.modelValue.includes(db.id)).length;
    stats[species] = { total, selected };
  });
  return stats;
});

// 当前显示的数据库
const currentDatabases = computed(() => {
  if (!selectedSpecies.value) return [];
  return groupedDatabases.value[selectedSpecies.value] || [];
});

// 按 sequence_type 分组当前物种的数据库（新增）
const databasesByType = computed(() => {
  const groups: Record<string, Database[]> = {};
  currentDatabases.value.forEach(db => {
    const type = db.sequence_type || 'unknown';
    if (!groups[type]) groups[type] = [];
    groups[type].push(db);
  });
  
  // 按预定义顺序排序
  const sortedTypes = Object.keys(groups).sort((a, b) => {
    return getTypeOrder(a) - getTypeOrder(b);
  });
  
  const sortedGroups: Record<string, Database[]> = {};
  sortedTypes.forEach(type => {
    sortedGroups[type] = groups[type];
  });
  
  return sortedGroups;
});

// 初始化选择第一个物种
if (filteredSpecies.value.length > 0 && selectedSpecies.value === null) {
  selectedSpecies.value = filteredSpecies.value[0] || null;
}

const toggleDb = (dbId: string) => {
  const newValue = [...props.modelValue];
  const index = newValue.indexOf(dbId);
  if (index === -1) {
    newValue.push(dbId);
  } else {
    newValue.splice(index, 1);
  }
  emit('update:modelValue', newValue);
};

const selectAllInSpecies = () => {
  if (!selectedSpecies.value) return;
  const targetDbs = groupedDatabases.value[selectedSpecies.value];
  if (!targetDbs) return;
  
  const dbIds = targetDbs.map(db => db.id);
  const newValue = Array.from(new Set([...props.modelValue, ...dbIds]));
  emit('update:modelValue', newValue);
};

const deselectAllInSpecies = () => {
  if (!selectedSpecies.value) return;
  const targetDbs = groupedDatabases.value[selectedSpecies.value];
  if (!targetDbs) return;

  const dbIds = targetDbs.map(db => db.id);
  emit('update:modelValue', props.modelValue.filter(id => !dbIds.includes(id)));
};

// 按类型全选（新增）
const selectAllByType = (type: string) => {
  const targetDbs = databasesByType.value[type];
  if (!targetDbs) return;
  
  const dbIds = targetDbs.map(db => db.id);
  const newValue = Array.from(new Set([...props.modelValue, ...dbIds]));
  emit('update:modelValue', newValue);
};

// 按类型取消选择（新增）
const deselectAllByType = (type: string) => {
  const targetDbs = databasesByType.value[type];
  if (!targetDbs) return;
  
  const dbIds = targetDbs.map(db => db.id);
  emit('update:modelValue', props.modelValue.filter(id => !dbIds.includes(id)));
};

const clearAll = () => {
  emit('update:modelValue', []);
};
</script>

<template>
  <div class="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm flex flex-col md:flex-row h-[500px]">
    <!-- Left Sidebar: Species List -->
    <div class="w-full md:w-64 border-b md:border-b-0 md:border-r border-gray-200 flex flex-col bg-gray-50/50">
      <div class="p-3 border-b border-gray-200 bg-white">
        <div class="relative">
          <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索物种..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
          />
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto">
        <button
          v-for="species in filteredSpecies"
          :key="species"
          @click="selectedSpecies = species"
          :class="[
            'w-full text-left px-4 py-3 text-sm flex items-center justify-between transition-all border-l-4 group',
            selectedSpecies === species 
              ? 'bg-primary-50 border-l-primary-600 text-primary-900 font-semibold' 
              : 'bg-white border-l-transparent text-gray-600 hover:bg-gray-50 hover:border-l-gray-300'
          ]"
        >
          <span class="truncate pr-2">{{ species }}</span>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span 
              :style="(statsPerSpecies[species]?.selected || 0) > 0
                ? 'background-color: #2563eb; color: white; min-width: 3.5rem;'
                : 'background-color: #f3f4f6; color: #4b5563; min-width: 2rem;'"
              class="px-2.5 py-1 rounded-full font-bold whitespace-nowrap text-center text-sm transition-colors shadow-sm"
            >
              <template v-if="(statsPerSpecies[species]?.selected || 0) > 0">
                {{ (statsPerSpecies[species]?.selected || 0) }}/{{ (statsPerSpecies[species]?.total || 0) }}
              </template>
              <template v-else>
                {{ (statsPerSpecies[species]?.total || 0) }}
              </template>
            </span>
          </div>
        </button>
        <div v-if="filteredSpecies.length === 0" class="p-8 text-center text-gray-400 text-xs italic">
          未找到相关物种
        </div>
      </div>
    </div>

    <!-- Right Content: Database List -->
    <div class="flex-1 flex flex-col min-w-0 bg-white">
      <div v-if="selectedSpecies && groupedDatabases[selectedSpecies]" class="flex flex-col h-full">
        <!-- Species Header -->
        <div class="p-4 border-b border-gray-100 flex items-center justify-between bg-white sticky top-0 z-10">
          <div>
            <h3 class="text-base font-bold text-gray-900">{{ selectedSpecies }}</h3>
            <p class="text-xs text-gray-500 mt-0.5">共 {{ statsPerSpecies[selectedSpecies]?.total || 0 }} 个数据库</p>
          </div>
          <div class="flex gap-2">
            <button 
              @click="selectAllInSpecies"
              class="text-[11px] font-medium text-primary-600 hover:text-primary-700 px-2 py-1 rounded hover:bg-primary-50 transition-colors border border-primary-100"
            >
              全选
            </button>
            <button 
              @click="deselectAllInSpecies"
              class="text-[11px] font-medium text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100 transition-colors border border-gray-200"
            >
              取消
            </button>
          </div>
        </div>

        <!-- Database Groups by Type -->
        <div class="flex-1 overflow-y-auto p-4 space-y-6">
          <div v-for="(databases, type) in databasesByType" :key="type" class="space-y-3">
            <!-- Type Group Header -->
            <div class="flex items-center justify-between pb-2 border-b border-gray-200">
              <h4 class="text-sm font-bold text-gray-700 uppercase tracking-wide">
                {{ getTypeLabel(type) }}
              </h4>
              <div class="flex gap-2">
                <button 
                  @click="selectAllByType(type)"
                  class="text-[10px] font-medium text-primary-600 hover:text-primary-700 px-1.5 py-0.5 rounded hover:bg-primary-50 transition-colors"
                >
                  全选
                </button>
                <button 
                  @click="deselectAllByType(type)"
                  class="text-[10px] font-medium text-gray-500 hover:text-gray-700 px-1.5 py-0.5 rounded hover:bg-gray-100 transition-colors"
                >
                  取消
                </button>
              </div>
            </div>

            <!-- Database Cards in This Type -->
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-3">
              <div
                v-for="db in databases"
                :key="db.id"
                @click="toggleDb(db.id)"
                :class="[
                  'p-3 rounded-lg border cursor-pointer flex items-center justify-between group transition-all',
                  modelValue.includes(db.id)
                    ? 'border-primary-500 bg-primary-50 shadow-sm ring-1 ring-primary-500/20'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 hover:shadow-sm'
                ]"
              >
                <div class="flex flex-col min-w-0 pr-2">
                  <!-- Main Title: genome_version or fallback to name -->
                  <span class="text-sm font-semibold truncate" :class="modelValue.includes(db.id) ? 'text-primary-700' : 'text-gray-800'">
                    {{ db.genome_version || db.name }}
                  </span>
                </div>
                <component 
                  :is="modelValue.includes(db.id) ? CheckCircle2 : Circle"
                  :class="[
                    'h-5 w-5 flex-shrink-0 transition-all',
                    modelValue.includes(db.id) ? '' : 'text-gray-300 group-hover:text-gray-400'
                  ]"
                  :style="modelValue.includes(db.id) ? 'color: #2563eb; fill: #dbeafe;' : ''"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Footer for selected info -->
        <div class="p-3 border-t border-gray-100 bg-gray-50/80 flex items-center justify-between text-xs">
          <span class="text-gray-500 font-medium">已选择 <span class="text-primary-600">{{ modelValue.length }}</span> 个数据库</span>
          <button 
            v-if="modelValue.length > 0"
            @click="clearAll"
            class="text-red-500 hover:text-red-600 flex items-center gap-1 font-medium transition-colors"
          >
            <XCircle class="h-3 w-3" />
            全部清空
          </button>
        </div>
      </div>
      <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 space-y-3">
        <Search class="h-10 w-10 text-gray-200" />
        <p class="text-sm italic">请从左侧选择一个物种</p>
      </div>
    </div>
  </div>
</template>
