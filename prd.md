# Product Requirements Document (PRD)
# Medical Q&A Chatbot with Accuracy Verification

## 1. Executive Summary

### 1.1 Product Overview
An AI-powered medical chatbot system designed to answer questions from patients and researchers with accuracy verification through human feedback. The system uses LLM agents and RAG (Retrieval-Augmented Generation) to provide evidence-based responses from scientific literature.

### 1.2 Target Users
- **Primary**: Medical researchers seeking recent publications and studies
- **Secondary**: Patients seeking medical information and education
- **Tertiary**: Medical professionals validating information accuracy

### 1.3 Business Goals
- Provide accurate, evidence-based medical information
- Reduce information retrieval time for medical research
- Build trust through human-verified response quality
- Create feedback loop for continuous accuracy improvement

## 2. Product Architecture

### 2.1 System Components
```
User Question → Intent Prediction → Vector DB Selection → RAG Retrieval →
Summarization → Human Feedback Collection → Quality Improvement Loop
```

### 2.2 Technology Stack
- **LLM Framework**: Agent-based architecture
- **Vector Database**: Multiple embedding DBs (QnA, Paper)
- **Search Integration**: Conditional PubMed API integration
- **Feedback System**: Web-based human evaluation interface

## 3. Feature Specifications

### Feature 1: Question Intent Prediction

**Objective**: Classify user questions to route to appropriate processing pipeline

**Input**: User question (natural language text)

**Output**: Intent classification label

**Implementation Strategy**:
- Few-shot prompting with intent examples
- Intent categories defined with:
  - Intent label (e.g., "RESEARCH")
  - Description (e.g., "논문 검색 요청")
  - Example utterances
  - Processing method (e.g., "조건부 PubMed검색")

**Example Intent Schema**:
```json
{
  "질문의도": "RESEARCH",
  "설명": "논문 검색 요청",
  "예시 발화": ["CKD 최신 연구", "논문 찾아줘"],
  "처리 방법": "조건부 PubMed검색"
}
```

**Sample Interaction**:
- Input: "신장병 관련 논문 궁금해"
- Output: "RESEARCH"

**Acceptance Criteria**:
- [ ] Correctly classifies 90%+ of test questions
- [ ] Response time < 2 seconds
- [ ] Supports multiple intent categories
- [ ] Handles ambiguous queries gracefully

---

### Feature 2: Vector Database Selection

**Objective**: Select appropriate embedding vector databases based on question intent and processing method

**Input**:
- Question intent (from Feature 1)
- Processing method

**Output**: Selected vector database(s)

**Implementation Strategy**:
- Calculate similarity scores across available vector DBs
- Apply configurable threshold for DB selection
- Support multi-DB selection (≥1 databases)

**Available Databases**:
- QnA embedding vector DB
- Paper embedding vector DB

**Example Flow**:
- Input: Intent="RESEARCH", Method="조건부 PubMed검색"
- Output: Paper embedding vector DB selected

**Acceptance Criteria**:
- [ ] Threshold-based selection working correctly
- [ ] Supports multiple simultaneous DB selection
- [ ] Selection logic is configurable
- [ ] Handles cases with no matching DB above threshold

---

### Feature 3: RAG (Retrieval-Augmented Generation)

**Objective**: Retrieve most relevant papers from selected vector database(s)

**Input**:
- Original user question
- Selected vector database(s)

**Output**: Top 5 most relevant papers

**Implementation Strategy**:
- Semantic similarity search using embeddings
- Rank by distance/similarity score
- Return configurable top-K results (default: 5)

**Retrieval Logic**:
- Query embedding generation
- Vector similarity calculation
- Ranking by closest distance
- Deduplication if multiple DBs selected

**Acceptance Criteria**:
- [ ] Returns exactly 5 papers (or fewer if insufficient matches)
- [ ] Retrieval time < 5 seconds
- [ ] Relevance score calculation is transparent
- [ ] Handles edge cases (no results, single result, etc.)

---

### Feature 4: Paper Summarization

**Objective**: Generate concise summaries of retrieved papers for user consumption

**Input**: Top 5 papers from RAG retrieval

**Output**: 5 paper summaries

**Implementation Strategy**:
- LLM-based abstractive summarization
- Consistent summary format across papers
- Key information extraction:
  - Main findings
  - Methodology overview
  - Clinical relevance
  - Publication metadata

**Summary Format**:
```
Title: [Paper Title]
Authors: [Author List]
Year: [Publication Year]
Summary: [2-3 sentence summary]
Key Findings: [Bullet points]
Relevance: [Relevance to user query]
```

**Acceptance Criteria**:
- [ ] Each summary is 100-150 words
- [ ] Maintains scientific accuracy
- [ ] Consistent formatting across all summaries
- [ ] Generation time < 10 seconds for all 5 summaries

---

### Feature 5: Human Feedback Data Collection

**Objective**: Aggregate all pipeline outputs for human evaluation

**Input**: All outputs from Features 1-4

**Output**: Structured data record for feedback system

**Data Schema**:
```json
{
  "question": "string (from Feature 1)",
  "intent": "string (Feature 1 output)",
  "selected_dbs": ["array (Feature 2 output)"],
  "retrieved_papers": ["array (Feature 3 output)"],
  "summaries": ["array (Feature 4 output)"],
  "timestamp": "ISO datetime",
  "feedback": null  // populated by Feature 6
}
```

**Storage Strategy**:
- Persistent storage (database/file system)
- Indexed by timestamp and question ID
- Queryable for analytics and reporting

**Acceptance Criteria**:
- [ ] All pipeline data captured completely
- [ ] Data persistence is reliable
- [ ] Query/retrieval interface available
- [ ] Data format is consistent and validated

---

### Feature 6: Human Feedback Interface

**Objective**: Web-based interface for quality evaluation of Q&A pairs

**Input**: Data from Feature 5

**Output**: Human feedback labels stored in data records

**Interface Layout**:

| Column 1: Question | Column 2: Summary | Column 3: Evaluation | Column 4: Metadata |
|-------------------|------------------|---------------------|-------------------|
| Original user question | 5 paper summaries | Feedback buttons | Intent, DBs, timestamp |

**Feedback Buttons**:
- ✅ **Good**: Response is accurate and helpful
- 🤔 **판단어려움**: Evaluation unclear or uncertain
- ❌ **Bad**: Response is inaccurate or unhelpful

**Workflow**:
1. Display question and summaries
2. User clicks evaluation button
3. Feedback saved to data record (3rd position in schema)
4. Record updated with feedback label
5. Next question/answer pair loaded

**Data Storage Order**:
```
[Question, Summaries, Evaluation, Intent, DBs, Papers, Timestamp, ...]
```

**Acceptance Criteria**:
- [ ] Interface displays all required information clearly
- [ ] Single-click feedback submission
- [ ] Feedback immediately saved to database
- [ ] Interface is responsive and accessible
- [ ] Supports pagination through multiple Q&A pairs
- [ ] Shows feedback statistics (e.g., 45% Good, 10% Bad, 45% 판단어려움)

---

## 4. Non-Functional Requirements

### 4.1 Performance
- End-to-end response time: < 20 seconds (question → summaries)
- System uptime: 99.5%
- Concurrent user support: 100+ simultaneous users

### 4.2 Scalability
- Vector DB should support millions of papers
- Horizontal scaling for LLM inference
- Feedback system should handle 10K+ evaluations/day

### 4.3 Security & Privacy
- HIPAA compliance considerations for patient data
- User question anonymization
- Secure feedback data storage
- Access control for feedback interface

### 4.4 Usability
- Mobile-responsive feedback interface
- Accessible design (WCAG 2.1 AA)
- Support for Korean and English languages
- Clear error messages and loading states

### 4.5 Reliability
- Fallback mechanisms for API failures
- Graceful degradation if vector DB unavailable
- Data backup and recovery procedures

## 5. Data Requirements

### 5.1 Vector Database Content
- **Paper DB**:
  - Embeddings of scientific papers (abstracts, full text)
  - Metadata: title, authors, journal, year, DOI
  - Source: PubMed, medical journals
  - Update frequency: Weekly

- **QnA DB**:
  - Embeddings of common medical Q&A pairs
  - Verified answers from medical professionals
  - Update frequency: Based on feedback analysis

### 5.2 Intent Training Data
- 100+ labeled question examples per intent category
- Diverse phrasing and medical terminology coverage
- Regular updates based on production query patterns

### 5.3 Feedback Data
- Retention: Indefinite (for model improvement)
- Privacy: Anonymized user identifiers
- Analytics: Aggregated quality metrics by intent/topic

## 6. User Stories

### US-1: Researcher Finding Recent Studies
**As a** medical researcher
**I want to** quickly find recent CKD studies
**So that** I can stay current with latest research

**Acceptance Criteria**:
- Search returns papers from last 2 years
- Results are ranked by relevance
- Summaries highlight key findings

### US-2: Patient Understanding Condition
**As a** patient with kidney disease
**I want to** understand my condition better
**So that** I can make informed health decisions

**Acceptance Criteria**:
- Responses use plain language
- Medical terminology is explained
- Sources are credible and recent

### US-3: Quality Evaluator Reviewing Responses
**As a** medical professional evaluating responses
**I want to** quickly assess answer quality
**So that** the system improves over time

**Acceptance Criteria**:
- Can evaluate 50+ responses in 30 minutes
- Evaluation options are clear
- Can see context (question + full summaries)

## 7. Success Metrics

### 7.1 Quality Metrics
- Human feedback "Good" rate: > 70%
- Human feedback "Bad" rate: < 15%
- Inter-rater reliability: > 0.75 (if multiple evaluators)

### 7.2 Usage Metrics
- Daily active users: 500+ researchers/patients
- Questions per session: 2.5+ average
- Return user rate: > 40%

### 7.3 Performance Metrics
- P95 response time: < 25 seconds
- System error rate: < 1%
- PubMed API success rate: > 98%

### 7.4 Business Metrics
- Cost per query: < $0.10
- Feedback completion rate: > 60% of responses
- Quality improvement trend: +5% quarterly

## 8. Development Phases

### Phase 1: MVP (8 weeks)
- Features 1-4: Core pipeline functionality
- Single vector DB (Paper)
- Single intent category (RESEARCH)
- Basic command-line interface

**Deliverables**:
- Working question → summary pipeline
- Manual evaluation spreadsheet
- Performance benchmarks

### Phase 2: Feedback System (4 weeks)
- Features 5-6: Data collection and web interface
- Multi-evaluator support
- Feedback analytics dashboard

**Deliverables**:
- Production feedback interface
- Database schema and storage
- Initial quality metrics

### Phase 3: Enhancement (6 weeks)
- Multiple intent categories
- QnA vector DB integration
- PubMed API integration
- Multi-language support

**Deliverables**:
- Full feature set operational
- Production deployment
- User documentation

### Phase 4: Optimization (Ongoing)
- Model fine-tuning based on feedback
- Performance optimization
- Feature expansion based on usage data

## 9. Technical Architecture

### 9.1 System Diagram
```
┌─────────────┐
│   User UI   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│   API Gateway/Backend   │
└──────┬──────────────────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│ Intent Agent │  │  RAG Engine  │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Few-Shot    │  │  Vector DBs  │
│  Prompts     │  │ (Paper, QnA) │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ PubMed API   │
                  │ (Conditional)│
                  └──────────────┘

┌─────────────────────────┐
│  Summarization Agent    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│   Feedback System       │
│  - Web Interface        │
│  - Data Collection      │
│  - Analytics            │
└─────────────────────────┘
```

### 9.2 Data Flow
1. **User Input** → Backend API
2. **Intent Classification** → Intent Agent (Few-shot LLM)
3. **DB Selection** → Similarity scoring across vector DBs
4. **Retrieval** → Vector search + optional PubMed API
5. **Summarization** → LLM-based summary generation
6. **Storage** → Feedback database
7. **Evaluation** → Human feedback interface
8. **Analytics** → Quality metrics and model improvement

### 9.3 Technology Recommendations

**Backend**:
- Python FastAPI or Node.js Express
- Async processing for long-running LLM calls
- Redis for caching intent classifications

**Vector Database**:
- Pinecone, Weaviate, or Qdrant
- Support for metadata filtering
- High-dimensional embedding support

**LLM Integration**:
- OpenAI GPT-4 or Anthropic Claude
- LangChain for agent orchestration
- Prompt templates versioned in code

**Frontend (Feedback Interface)**:
- React or Vue.js
- Responsive design framework (Tailwind CSS)
- Real-time updates for collaborative evaluation

**Storage**:
- PostgreSQL for structured feedback data
- S3/Cloud Storage for document storage
- Time-series DB for analytics

## 10. Risk Assessment

### 10.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucination in summaries | High | Medium | Human verification, confidence scores |
| Vector DB retrieval irrelevance | High | Medium | Hybrid search (semantic + keyword) |
| PubMed API rate limits | Medium | Low | Caching, request queuing |
| Slow response times | Medium | Medium | Caching, async processing, optimization |

### 10.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low user adoption | High | Medium | User research, iterative design |
| Insufficient feedback data | Medium | Medium | Incentivize evaluators, simplify interface |
| Medical accuracy concerns | Critical | Low | Disclaimers, medical professional review |
| Cost overruns (LLM API) | Medium | Medium | Query optimization, caching strategy |

### 10.3 Compliance Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| HIPAA violations | Critical | Low | Legal review, anonymization |
| Medical misinformation liability | High | Medium | Clear disclaimers, source citations |
| Copyright issues (papers) | Medium | Low | Fair use compliance, abstracts only |

## 11. Dependencies

### 11.1 External Dependencies
- PubMed API access and reliability
- LLM provider (OpenAI/Anthropic) API availability
- Vector database provider uptime
- Medical paper access rights

### 11.2 Internal Dependencies
- Medical professional availability for feedback
- Annotation/evaluation team capacity
- DevOps infrastructure for deployment

### 11.3 Third-Party Services
- Authentication provider (if required)
- Monitoring and logging (Datadog, Sentry)
- Analytics platform (Mixpanel, Amplitude)

## 12. Assumptions

1. Medical professionals are available for feedback evaluation
2. PubMed API is sufficient for research paper retrieval
3. Users have reliable internet connectivity
4. English and Korean language support is sufficient initially
5. Pre-existing paper embeddings are available or can be generated
6. Legal/compliance review approved before production launch

## 13. Out of Scope (Phase 1)

- Real-time chat interface (batch Q&A only)
- User authentication and personalization
- Multi-modal inputs (images, voice)
- Direct doctor consultation features
- Mobile native applications
- Integration with electronic health records (EHR)
- Automated medical diagnosis or treatment recommendations

## 14. Open Questions

1. What is the exact scope of medical domains covered? (All medicine vs specific specialties)
2. Who are the authorized feedback evaluators? (Credentials required?)
3. What is the data retention policy for user questions?
4. Should the system provide confidence scores with summaries?
5. How often should vector databases be updated with new papers?
6. What languages should be supported beyond Korean and English?
7. Should users see feedback statistics for transparency?

## 15. Appendix

### 15.1 Glossary
- **RAG**: Retrieval-Augmented Generation - technique combining retrieval with LLM generation
- **Vector DB**: Database optimized for similarity search using embeddings
- **Intent Classification**: Categorizing user input by intended action/goal
- **Few-shot Learning**: Providing examples to guide LLM behavior
- **Embedding**: Numerical vector representation of text for similarity comparison

### 15.2 References
- Original functional specification: `fuction specification.md`
- PubMed API documentation: https://www.ncbi.nlm.nih.gov/home/develop/api/
- Medical information accuracy standards: [To be added]

### 15.3 Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-05 | Claude Code | Initial PRD creation from functional spec |

---

**Document Owner**: Medical AI Product Team
**Last Updated**: 2025-11-05
**Status**: Draft for Review
