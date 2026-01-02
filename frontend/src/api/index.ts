import axios from 'axios';
import type { Database, ToolInfo, JobStatus } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: API_URL,
});

export const api = {
    async getDatabases(): Promise<Database[]> {
        const { data } = await client.get('/api/databases');
        return data;
    },

    async getTools(): Promise<ToolInfo[]> {
        const { data } = await client.get('/api/tools');
        return data;
    },

    async uploadAlignmentFile(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        const { data } = await client.post('/api/databases/upload', formData);
        return data;
    },

    async submitJob(payload: {
        query_filename?: string;
        query_sequence?: string;
        db_ids: string[];
        tool: string;
        options?: any;
    }): Promise<JobStatus> {
        const { data } = await client.post('/api/jobs/', payload);
        return data;
    },

    async getJobStatus(jobId: string): Promise<JobStatus> {
        const { data } = await client.get(`/api/jobs/${jobId}`);
        return data;
    },
};
