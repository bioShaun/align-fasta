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
        class="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-bold border border-slate-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Download class="w-4 h-4" />
        下载表格 (TSV)
      </button>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-x-auto">
      <table class="w-full text-left text-sm border-collapse min-w-[1200px]">
        <thead>
          <!-- BLAST outfmt 6 header -->
          <tr v-if="tool === 'blast'" class="bg-slate-800/80 text-slate-400 font-bold border-b border-slate-700">
            <th class="px-3 py-4">数据库</th>
            <th class="px-3 py-4">qseqid</th>
            <th class="px-3 py-4">sseqid</th>
            <th class="px-3 py-4 text-center">pident</th>
            <th class="px-3 py-4 text-center">length</th>
            <th class="px-3 py-4 text-center">mismatch</th>
            <th class="px-3 py-4 text-center">gapopen</th>
            <th class="px-3 py-4 text-center">qstart</th>
            <th class="px-3 py-4 text-center">qend</th>
            <th class="px-3 py-4 text-center">sstart</th>
            <th class="px-3 py-4 text-center">send</th>
            <th class="px-3 py-4">evalue</th>
            <th class="px-3 py-4 text-center">bitscore</th>
          </tr>
          <!-- Minimap2 header -->
          <tr v-else class="bg-slate-800/80 text-slate-400 font-bold border-b border-slate-700">
            <th class="px-3 py-4">数据库</th>
            <th class="px-3 py-4">查询序列</th>
            <th class="px-3 py-4">目标序列</th>
            <th class="px-3 py-4 text-center">查询长度</th>
            <th class="px-3 py-4 text-center">目标长度</th>
            <th class="px-3 py-4">查询范围</th>
            <th class="px-3 py-4">目标范围</th>
            <th class="px-3 py-4 text-center">链</th>
            <th class="px-3 py-4 text-center">匹配数</th>
            <th class="px-3 py-4 text-center">区块长度</th>
            <th class="px-3 py-4 text-center">MapQ</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-850">
          <tr v-for="(hit, idx) in hits" :key="idx" class="hover:bg-indigo-500/5 transition-colors group">
            <td class="px-3 py-3">
              <div class="flex items-center gap-1.5 px-2 py-1 bg-slate-800/50 rounded-lg border border-slate-700 text-[10px] text-slate-400 font-bold whitespace-nowrap">
                <DatabaseIcon class="w-3 h-3 text-indigo-400" />
                {{ hit.database }}
              </div>
            </td>
            <!-- BLAST outfmt 6 row -->
            <template v-if="tool === 'blast'">
              <td class="px-3 py-3 text-xs text-indigo-300 font-mono truncate max-w-[100px]">{{ hit.qseqid }}</td>
              <td class="px-3 py-3 font-mono text-indigo-400 font-bold">{{ hit.sseqid }}</td>
              <td class="px-3 py-3 text-center">
                <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300">{{ hit.pident }}%</span>
              </td>
              <td class="px-3 py-3 text-slate-300 text-center font-mono">{{ hit.length }}</td>
              <td class="px-3 py-3 text-slate-500 text-center font-mono">{{ hit.mismatch }}</td>
              <td class="px-3 py-3 text-slate-500 text-center font-mono">{{ hit.gapopen }}</td>
              <td class="px-3 py-3 text-slate-400 text-center font-mono">{{ hit.qstart }}</td>
              <td class="px-3 py-3 text-slate-400 text-center font-mono">{{ hit.qend }}</td>
              <td class="px-3 py-3 text-slate-400 text-center font-mono">{{ hit.sstart }}</td>
              <td class="px-3 py-3 text-slate-400 text-center font-mono">{{ hit.send }}</td>
              <td class="px-3 py-3 text-emerald-400 font-mono">{{ formatEval(hit.evalue) }}</td>
              <td class="px-3 py-3 text-amber-300 font-mono text-center font-bold">{{ hit.bitscore?.toFixed(1) }}</td>
            </template>
            <!-- Minimap2 row -->
            <template v-else>
              <td class="px-3 py-3 text-xs text-purple-300 font-mono truncate max-w-[100px]">{{ hit.query_name }}</td>
              <td class="px-3 py-3 font-mono text-purple-400 font-bold">{{ hit.target_name }}</td>
              <td class="px-3 py-3 text-slate-400 text-center">{{ hit.query_len }}</td>
              <td class="px-3 py-3 text-slate-400 text-center">{{ hit.target_len }}</td>
              <td class="px-3 py-3 text-xs text-slate-300 font-mono">{{ hit.query_start }}-{{ hit.query_end }}</td>
              <td class="px-3 py-3 text-xs text-slate-300 font-mono">{{ hit.target_start }}-{{ hit.target_end }}</td>
              <td class="px-3 py-3 text-center">
                <span :class="[
                  'px-2 py-0.5 rounded text-[10px] font-black uppercase',
                  hit.strand === '+' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                ]">
                  {{ hit.strand === '+' ? '正链' : '负链' }}
                </span>
              </td>
              <td class="px-3 py-3 text-emerald-400 font-mono text-center font-bold">{{ hit.matches }}</td>
              <td class="px-3 py-3 text-slate-500 font-mono text-center">{{ hit.block_len }}</td>
              <td class="px-3 py-3 text-center">
                <div class="inline-flex items-center gap-1.5">
                  <div class="h-1.5 w-1.5 rounded-full" :class="hit.mapq! > 30 ? 'bg-emerald-500' : 'bg-amber-500'"></div>
                  <span class="text-slate-300 font-mono font-bold">{{ hit.mapq }}</span>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
      <div v-if="hits.length === 0" class="p-20 text-center text-slate-500 bg-slate-900/50">
        <Info class="w-12 h-12 mx-auto mb-4 opacity-10" />
        没有找到任何比对结果。
      </div>
    </div>

    <!-- Column Explanations Section -->
    <div class="bg-slate-900/30 border border-slate-800 p-6 rounded-2xl">
      <h3 class="text-sm font-bold text-slate-400 flex items-center gap-2 mb-4">
        <HelpCircle class="w-4 h-4 text-indigo-400" />
        {{ tool === 'blast' ? 'BLAST 比对结果列说明' : 'Minimap2 比对结果列说明' }} (参照标准格式)
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <template v-if="tool === 'blast'">
          <div class="space-y-2">
            <p class="text-xs"><b class="text-indigo-400 font-mono">数据库:</b> 目标参考序列所在的数据库名称</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">qseqid:</b> 查询序列 ID</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">sseqid:</b> 目标序列 ID (Subject)</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">pident:</b> 一致性百分比</p>
          </div>
          <div class="space-y-2">
            <p class="text-xs"><b class="text-indigo-400 font-mono">length:</b> 比对区域长度</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">mismatch:</b> 错配碱基数</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">gapopen:</b> 缺口数量</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">qstart/qend:</b> 查询序列起止位置</p>
          </div>
          <div class="space-y-2">
            <p class="text-xs"><b class="text-indigo-400 font-mono">sstart/send:</b> 目标序列起止位置</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">evalue:</b> 期望值，越小越显著</p>
            <p class="text-xs"><b class="text-indigo-400 font-mono">bitscore:</b> 比对得分</p>
          </div>
        </template>
        <template v-else>
          <div class="space-y-2">
            <p class="text-xs"><b class="text-purple-400 font-mono">数据库:</b> 目标参考序列所在的数据库名称</p>
            <p class="text-xs"><b class="text-purple-400 font-mono">MapQ:</b> 比对质量分数 (0-60)</p>
            <p class="text-xs"><b class="text-purple-400 font-mono">匹配数:</b> 匹配的碱基总数</p>
          </div>
          <div class="space-y-2">
            <p class="text-xs"><b class="text-purple-400 font-mono">区块长度:</b> 比对区域总长度</p>
            <p class="text-xs"><b class="text-purple-400 font-mono">链:</b> 正链(+)或负链(-)</p>
            <p class="text-xs"><b class="text-purple-400 font-mono">长度:</b> 查询/目标序列总长度</p>
          </div>
          <div class="space-y-2">
            <p class="text-xs"><b class="text-purple-400 font-mono">范围:</b> 查询/目标序列的比对起止位置</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.divide-slate-850 > :not([hidden]) ~ :not([hidden]) {
  border-color: rgba(30, 41, 59, 0.5);
}
</style>
