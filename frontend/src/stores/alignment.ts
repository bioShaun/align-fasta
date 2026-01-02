import { defineStore } from 'pinia';
import { api } from '../api';
import type { Database, ToolInfo, JobStatus } from '../types';

export const useAlignmentStore = defineStore('alignment', {
    state: () => ({
        databases: [] as Database[],
        tools: [] as ToolInfo[],
        activeJobs: [] as JobStatus[],
        loading: false,
        error: null as string | null,
    }),

    actions: {
        async fetchDatabases() {
            this.loading = true;
            try {
                this.databases = await api.getDatabases();
            } catch (err: any) {
                this.error = 'Failed to fetch databases';
            } finally {
                this.loading = false;
            }
        },

        async fetchTools() {
            try {
                this.tools = await api.getTools();
            } catch (err: any) {
                this.error = 'Failed to fetch tools';
            }
        },

        async submitAlignment(input: File | string, dbIds: string[], tool: string, options: any = {}) {
            this.loading = true;
            try {
                let job;
                if (typeof input === 'string') {
                    // Submit directly as sequence
                    job = await api.submitJob({
                        query_sequence: input,
                        db_ids: dbIds,
                        tool,
                        options
                    });
                } else {
                    // Upload file first
                    const uploadRes = await api.uploadAlignmentFile(input);
                    job = await api.submitJob({
                        query_filename: uploadRes.filename,
                        db_ids: dbIds,
                        tool,
                        options
                    });
                }

                this.activeJobs.push(job);
                return job;
            } catch (err: any) {
                this.error = 'Failed to submit job';
                throw err;
            } finally {
                this.loading = false;
            }
        },

        async updateDatabase(id: string, update: {
            species?: string;
            genome_version?: string;
            sequence_type?: string;
            description?: string;
        }) {
            try {
                await api.updateDatabase(id, update);
                await this.fetchDatabases();
            } catch (err: any) {
                this.error = 'Failed to update database';
            }
        },

        async deleteDatabase(id: string) {
            try {
                await api.deleteDatabase(id);
                await this.fetchDatabases();
            } catch (err: any) {
                this.error = 'Failed to delete database';
            }
        },

        async createIndex(id: string, tool: string) {
            try {
                await api.createIndex(id, tool);
                // We don't wait for the background indexing to finish here
                // but we might want to poll or refresh later
                setTimeout(() => this.fetchDatabases(), 2000);
            } catch (err: any) {
                this.error = 'Failed to create index';
            }
        },

        async uploadReference(file: File) {
            this.loading = true;
            try {
                await api.uploadReference(file);
                await this.fetchDatabases();
            } catch (err: any) {
                this.error = 'Failed to upload reference';
            } finally {
                this.loading = false;
            }
        },

        async fetchJobStatus(jobId: string) {
            try {
                const job = await api.getJobStatus(jobId);
                const index = this.activeJobs.findIndex(j => j.job_id === jobId);
                if (index !== -1) {
                    this.activeJobs[index] = job;
                } else {
                    this.activeJobs.push(job);
                }
                return job;
            } catch (err: any) {
                this.error = 'Failed to fetch job status';
                throw err;
            }
        }
    }
});
