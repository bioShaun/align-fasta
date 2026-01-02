# Project Tasks

## Phase 1: Prototype (MVP)
- [x] **Setup Project Structure**
    - [x] Initialize project directory structure
    - [x] Create Docker Compose configuration
    - [x] Setup FastAPI backend skeleton
- [/] **Implement Backend API**
    - [x] Basic FastAPI app with CORS
    - [x] File upload endpoint
    - [ ] Database management endpoints (list, create, delete)
    - [ ] Input validation and error handling
- [ ] **Integrate BLAST**
    - [ ] Implement BLAST wrapper (blastn, blastp)
    - [ ] Implement makeblastdb for indexing
    - [ ] Parse BLAST JSON output
- [ ] **Setup Vue 3 Frontend**
    - [ ] Initialize Vue 3 + Vite project
    - [ ] Configure Tailwind CSS
    - [ ] Create basic layout and routing
    - [ ] Implement database list view
    - [ ] Implement query submission form
    - [ ] Display raw results

## Phase 2: Asynchronous Jobs & Production Readiness
- [/] **Implement Job Queue**
    - [x] Setup Celery with Redis
    - [x] Basic task structure
    - [ ] Job status tracking and persistence
    - [ ] Result storage and retrieval
- [ ] **Integrate Minimap2**
    - [ ] Implement Minimap2 wrapper
    - [ ] Implement minimap2 indexing
    - [ ] Parse PAF output
- [ ] **Frontend Job Monitor**
    - [ ] Job status polling
    - [ ] Job history list
    - [ ] Result display components

## Phase 3: Advanced UI & Visualization
- [ ] **Results Visualization**
    - [ ] BLAST hit table component
    - [ ] Query coverage graphic
    - [ ] Minimap2 dotplot visualization
- [ ] **Admin Panel**
    - [ ] Database management UI
    - [ ] Index creation interface
    - [ ] File cleanup tools

## Phase 4: Polish & Deployment
- [ ] **Error Handling & UX**
    - [ ] Comprehensive error messages
    - [ ] Loading states and feedback
    - [ ] Input validation on frontend
- [ ] **Documentation**
    - [ ] API documentation (Swagger)
    - [ ] User guide
    - [ ] Deployment guide
- [ ] **Testing**
    - [ ] Backend unit tests
    - [ ] Frontend component tests
    - [ ] E2E tests for critical flows
- [ ] **Docker Optimization**
    - [ ] Multi-stage builds
    - [ ] Health checks
    - [ ] Production configuration
