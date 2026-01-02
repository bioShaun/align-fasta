export interface Database {
    id: string;
    name: string;
    path: string;
    indexed: boolean;
    tools: string[];
    // 元数据字段
    species?: string;
    genome_version?: string;
    sequence_type?: string;  // 'cds' | 'protein' | 'genome' | 'transcript'
    description?: string;
}

export interface ToolInfo {
    name: string;
    description: string;
}

export interface JobStatus {
    job_id: string;
    state: string;
    status: string | null;
    result: any | null;
}

export interface AlignmentHit {
    // BLAST outfmt 6 columns
    qseqid?: string;
    sseqid?: string;
    pident?: number;
    length?: number;
    mismatch?: number;
    gapopen?: number;
    qstart?: number;
    qend?: number;
    sstart?: number;
    send?: number;
    evalue?: number;
    bitscore?: number;
    // BLAST extra
    stitle?: string;
    qlen?: number;

    // Minimap2 specific
    query_name?: string;
    query_len?: number;
    query_start?: number;
    query_end?: number;
    strand?: string;
    target_name?: string;
    target_len?: number;
    target_start?: number;
    target_end?: number;
    matches?: number;
    block_len?: number;
    mapq?: number;
    // Multi-db support
    database?: string;
}
