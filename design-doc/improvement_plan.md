# UI and Output Improvements Plan

## Issues Identified

### Issue 1: Frontend Blank Space (Missing Checkbox) - ✅ FIXED
The checkbox UI was added successfully.

### Issue 2: Multi-Sequence Results Missing - ✅ FIXED
Backend now parses all query results. Frontend shows "Query" column.

---

## NEW: Root Cause of "0 Hits" Issue

### Problem
The watcher in `App.vue` auto-enables "Short Query Optimization" for **all sequences < 200 characters**:

```typescript
watch(queryText, (newVal) => {
  if (newVal.length > 0 && newVal.length < 200) {
    useShortQuery.value = true;  // Always sets to true, never false
  }
});
```

### Why This Causes 0 Hits
1. User's 107bp sequence has ~113 characters total (including `>1\n`)
2. This is less than 200, so `blastn-short` is **automatically enabled**
3. `blastn-short` is optimized for < 50bp sequences
4. Using it on longer sequences often returns **0 hits**

### Why It Never Resets
The watcher only sets `true`, never `false`. Once enabled, it stays enabled even if user inputs long sequences.

---

## Modification Plan

### Fix: Correct the watcher logic

**File:** `frontend/src/App.vue` (lines 16-22)

**Current Code (Buggy):**
```typescript
watch(queryText, (newVal) => {
  if (newVal.length > 0 && newVal.length < 200) {
    useShortQuery.value = true;
  }
});
```

**Fixed Code:**
```typescript
watch(queryText, (newVal) => {
  // Parse FASTA to get actual sequence length (excluding headers)
  const sequences = newVal.split(/^>/m).filter(Boolean);
  let maxSeqLen = 0;
  for (const seq of sequences) {
    const lines = seq.split('\n').slice(1);
    const seqLen = lines.join('').replace(/\s/g, '').length;
    maxSeqLen = Math.max(maxSeqLen, seqLen);
  }
  // Only enable for actual short sequences (< 50bp)
  useShortQuery.value = maxSeqLen > 0 && maxSeqLen < 50;
});
```

**Key Changes:**
1. Parse FASTA format to extract actual sequence (exclude `>header` lines)
2. Calculate real nucleotide count
3. Threshold changed from 200 chars to **50bp** (matches UI label)
4. Sets `false` when sequence is long (bidirectional toggle)

---

## Task List

- [x] Fix 1: Add Short Query checkbox UI to App.vue template
- [x] Fix 2: Update blast.py to parse all query results
- [x] Fix 3: Add query_name to AlignmentHit type
- [x] Fix 4: Update ResultTable.vue to show Query column
- [ ] **Fix 5: Correct watcher logic to use actual sequence length**
- [ ] Test with short sequence (< 50bp) - should auto-check
- [ ] Test with long sequence (> 50bp) - should auto-uncheck
