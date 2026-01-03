<script setup lang="ts">
import type { AlignmentHit } from '../types';
import { Info, HelpCircle, Download, Database as DatabaseIcon } from 'lucide-vue-next';

const props = defineProps<{
  hits: AlignmentHit[];
  tool: string;
}>();

const formatEval = (val?: number) => {
  if (val === undefined || val === null) return '-';
  if (val === 0) return '0.0';
  if (val < 0.001) return val.toExponential(2);
  return val.toFixed(4);
};

// Download as TSV (outfmt 6 style) - using Blob URL for better compatibility
const downloadTSV = () => {
  if (props.hits.length === 0) return;

  let header: string;
  let rows: string[];

  if (props.tool === 'blast') {
    header = ['database', 'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore'].join('\t');
    rows = props.hits.map(h => [
      h.database ?? '',
      h.qseqid ?? '',
      h.sseqid ?? '',
      h.pident ?? '',
      h.length ?? '',
      h.mismatch ?? '',
      h.gapopen ?? '',
      h.qstart ?? '',
      h.qend ?? '',
      h.sstart ?? '',
      h.send ?? '',
      h.evalue ?? '',
      h.bitscore ?? ''
    ].join('\t'));
  } else {
    header = ['database', 'query_name', 'target_name', 'query_len', 'target_len', 'query_start', 'query_end', 'target_start', 'target_end', 'strand', 'matches', 'block_len', 'mapq'].join('\t');
    rows = props.hits.map(h => [
      h.database ?? '',
      h.query_name ?? '',
      h.target_name ?? '',
      h.query_len ?? '',
      h.target_len ?? '',
      h.query_start ?? '',
      h.query_end ?? '',
      h.target_start ?? '',
      h.target_end ?? '',
      h.strand ?? '',
      h.matches ?? '',
      h.block_len ?? '',
      h.mapq ?? ''
    ].join('\t'));
  }

  // Add BOM for Excel UTF-8 compatibility
  const content = '\uFEFF' + [header, ...rows].join('\n');
  
  // Use Blob URL instead of Data URL for better Chrome compatibility and large file support
  const blob = new Blob([content], { type: 'text/tab-separated-values;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  a.download = `alignment_${props.tool}_${timestamp}.tsv`;
  
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
</script>

<template>
  <div class="space-y-6">
    <!-- Download Button -->
    <div class="flex justify-end">
      <button 
        @click="downloadTSV"
        :disabled="hits.length === 0"
        class="flex items-center gap-2 px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 rounded-lg text-sm font-bold border border-gray-200 shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
      >
        <Download class="w-4 h-4 text-primary-600" />
        导出报告 (TSV)
      </button>
    </div>

    <div class="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm overflow-x-auto">
      <table class="w-full text-left text-sm border-collapse min-w-[1200px]">
        <thead>
          <!-- BLAST outfmt 6 header -->
          <tr v-if="tool === 'blast'" class="bg-gray-50 text-gray-500 font-bold border-b border-gray-200">
            <th class="px-4 py-3.5">数据库</th>
            <th class="px-4 py-3.5">qseqid</th>
            <th class="px-4 py-3.5">sseqid</th>
            <th class="px-4 py-3.5 text-center">pident</th>
            <th class="px-4 py-3.5 text-center">length</th>
            <th class="px-4 py-3.5 text-center">mismatch</th>
            <th class="px-4 py-3.5 text-center">gapopen</th>
            <th class="px-4 py-3.5 text-center">qstart</th>
            <th class="px-4 py-3.5 text-center">qend</th>
            <th class="px-4 py-3.5 text-center">sstart</th>
            <th class="px-4 py-3.5 text-center">send</th>
            <th class="px-4 py-3.5">evalue</th>
            <th class="px-4 py-3.5 text-center">bitscore</th>
          </tr>
          <!-- Minimap2 header -->
          <tr v-else class="bg-gray-50 text-gray-500 font-bold border-b border-gray-200">
            <th class="px-4 py-3.5">数据库</th>
            <th class="px-4 py-3.5">查询序列</th>
            <th class="px-4 py-3.5">目标序列</th>
            <th class="px-4 py-3.5 text-center">查询长度</th>
            <th class="px-4 py-3.5 text-center">目标长度</th>
            <th class="px-4 py-3.5">查询范围</th>
            <th class="px-4 py-3.5">目标范围</th>
            <th class="px-4 py-3.5 text-center">链</th>
            <th class="px-4 py-3.5 text-center">匹配数</th>
            <th class="px-4 py-3.5 text-center">区块长度</th>
            <th class="px-4 py-3.5 text-center">MapQ</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="(hit, idx) in hits" :key="idx" class="hover:bg-primary-50/30 transition-colors group">
            <td class="px-4 py-3">
              <div class="flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded text-[10px] text-gray-600 font-bold whitespace-nowrap border border-gray-200">
                <DatabaseIcon class="w-3 h-3 text-primary-500" />
                {{ hit.database }}
              </div>
            </td>
            <!-- BLAST outfmt 6 row -->
            <template v-if="tool === 'blast'">
              <td class="px-4 py-3 text-xs text-gray-500 font-mono truncate max-w-[120px]">{{ hit.qseqid }}</td>
              <td class="px-4 py-3 font-mono text-primary-700 font-bold">{{ hit.sseqid }}</td>
              <td class="px-4 py-3 text-center">
                <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100">{{ hit.pident }}%</span>
              </td>
              <td class="px-4 py-3 text-gray-700 text-center font-mono">{{ hit.length }}</td>
              <td class="px-4 py-3 text-gray-400 text-center font-mono">{{ hit.mismatch }}</td>
              <td class="px-4 py-3 text-gray-400 text-center font-mono">{{ hit.gapopen }}</td>
              <td class="px-4 py-3 text-gray-500 text-center font-mono">{{ hit.qstart }}</td>
              <td class="px-4 py-3 text-gray-500 text-center font-mono">{{ hit.qend }}</td>
              <td class="px-4 py-3 text-gray-500 text-center font-mono">{{ hit.sstart }}</td>
              <td class="px-4 py-3 text-gray-500 text-center font-mono">{{ hit.send }}</td>
              <td class="px-4 py-3 text-emerald-600 font-mono font-medium">{{ formatEval(hit.evalue) }}</td>
              <td class="px-4 py-3 text-amber-700 font-mono text-center font-bold">{{ hit.bitscore?.toFixed(1) }}</td>
            </template>
            <!-- Minimap2 row -->
            <template v-else>
              <td class="px-4 py-3 text-xs text-gray-500 font-mono truncate max-w-[120px]">{{ hit.query_name }}</td>
              <td class="px-4 py-3 font-mono text-primary-700 font-bold">{{ hit.target_name }}</td>
              <td class="px-4 py-3 text-gray-500 text-center">{{ hit.query_len }}</td>
              <td class="px-4 py-3 text-gray-500 text-center">{{ hit.target_len }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 font-mono">{{ hit.query_start }}-{{ hit.query_end }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 font-mono">{{ hit.target_start }}-{{ hit.target_end }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="[
                  'px-2 py-0.5 rounded text-[10px] font-bold uppercase border',
                  hit.strand === '+' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-rose-50 text-rose-700 border-rose-100'
                ]">
                  {{ hit.strand === '+' ? '正链' : '负链' }}
                </span>
              </td>
              <td class="px-4 py-3 text-emerald-600 font-mono text-center font-bold">{{ hit.matches }}</td>
              <td class="px-4 py-3 text-gray-400 font-mono text-center">{{ hit.block_len }}</td>
              <td class="px-4 py-3 text-center">
                <div class="inline-flex items-center gap-1.5">
                  <div class="h-1.5 w-1.5 rounded-full" :class="hit.mapq! > 30 ? 'bg-emerald-500' : 'bg-amber-500'"></div>
                  <span class="text-gray-700 font-mono font-bold">{{ hit.mapq }}</span>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
      <div v-if="hits.length === 0" class="p-20 text-center text-gray-400 bg-gray-50/50">
        <Info class="w-12 h-12 mx-auto mb-4 opacity-10" />
        没有找到任何符合条件的比对结果。
      </div>
    </div>

    <!-- Column Explanations Section -->
    <div class="bg-white border border-gray-200 p-6 rounded-xl">
      <h3 class="text-sm font-bold text-gray-700 flex items-center gap-2 mb-4">
        <HelpCircle class="w-4 h-4 text-primary-600" />
        {{ tool === 'blast' ? 'BLAST 比对结果列说明' : 'Minimap2 比对结果列说明' }}
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-4 gap-x-8">
        <template v-if="tool === 'blast'">
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">数据库:</b> 目标序列所属库</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">qseqid:</b> 查询序列名称</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">sseqid:</b> 命中目标 ID</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">pident:</b> 序列一致性分数</p>
          </div>
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">length:</b> 比对覆盖范围长度</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">mismatch:</b> 错误匹配计数</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">gapopen:</b> 缺口引入次数</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">qstart/end:</b> 查询坐标信息</p>
          </div>
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">sstart/end:</b> 目标坐标信息</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">evalue:</b> 统计期望值</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">bitscore:</b> 归一化得分</p>
          </div>
        </template>
        <template v-else>
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">数据库:</b> 目标序列所属库</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">MapQ:</b> 平均比对质量</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">匹配数:</b> 有效匹配碱基</p>
          </div>
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">区块长度:</b> 全比对区域长</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">链:</b> 正向(+)或反向(-)</p>
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">长度:</b> 序列总长信息</p>
          </div>
          <div class="space-y-3">
            <p class="text-xs text-gray-600"><b class="text-gray-900 font-mono">范围:</b> 起止坐标信息</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Clearer table styling */
table th {
  white-space: nowrap;
}
</style>
