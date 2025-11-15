# System Diagrams

This document contains visual diagrams for the AI Code Review Agent system.

## High-Level System Flow

```mermaid
flowchart TD
    A[User Input] --> B{Review Mode?}
    B -->|Local| C[Git Utils]
    B -->|PR| D[Bitbucket API]
    
    C --> E[Get Changed Files]
    D --> F[Get PR Changes]
    
    E --> G[File Processing Loop]
    F --> G
    
    G --> H[Load Standards]
    H --> I[Load Custom Guidelines]
    I --> J[Build Context]
    
    J --> K[Create AI Agent]
    K --> L[Generate Prompt]
    L --> M[AWS Bedrock]
    
    M --> N[Claude 3.5 Sonnet]
    N --> O[JSON Response]
    
    O --> P[Parse & Validate]
    P --> Q{Valid Response?}
    
    Q -->|No| R[Error Handling]
    Q -->|Yes| S[Filter by Severity]
    
    S --> T{PR Mode?}
    T -->|Yes| U[Add PR Comments]
    T -->|No| V[Display Results]
    
    U --> W[Review Complete]
    V --> W
    R --> W
```

## Detailed Processing Flow

```mermaid
flowchart LR
    subgraph "Input Layer"
        A1[CLI Args]
        A2[API Request]
        A3[Web UI]
    end
    
    subgraph "Configuration"
        B1[Environment Variables]
        B2[Review Standards YAML]
        B3[Custom Guidelines MD]
    end
    
    subgraph "Core Processing"
        C1[Code Reviewer]
        C2[Agent Factory]
        C3[Task Builder]
    end
    
    subgraph "External Services"
        D1[Git Repository]
        D2[Bitbucket Server]
        D3[AWS Bedrock]
    end
    
    subgraph "Output Layer"
        E1[Console Output]
        E2[PR Comments]
        E3[API Response]
        E4[Debug Files]
    end
    
    A1 --> C1
    A2 --> C1
    A3 --> C1
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
    
    C1 --> C2
    C2 --> C3
    
    C1 --> D1
    C1 --> D2
    C3 --> D3
    
    C1 --> E1
    C1 --> E2
    C1 --> E3
    C1 --> E4
```

## Data Processing Pipeline

```mermaid
flowchart TD
    subgraph "File Discovery"
        A1[Scan Repository]
        A2[Filter File Types]
        A3[Get File List]
    end
    
    subgraph "Content Extraction"
        B1[Read File Content]
        B2[Generate Diff]
        B3[Extract Metadata]
    end
    
    subgraph "Context Building"
        C1[Merge Standards]
        C2[Add Custom Guidelines]
        C3[Format Prompt]
    end
    
    subgraph "AI Processing"
        D1[Send to Bedrock]
        D2[Process with Claude]
        D3[Return JSON]
    end
    
    subgraph "Result Processing"
        E1[Parse JSON]
        E2[Validate Structure]
        E3[Filter Severity]
        E4[Format Output]
    end
    
    A1 --> A2 --> A3
    A3 --> B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3
    C3 --> D1 --> D2 --> D3
    D3 --> E1 --> E2 --> E3 --> E4
```

## Component Interaction Diagram

```mermaid
graph TB
    subgraph "User Interfaces"
        UI1[CLI Interface]
        UI2[Web API]
        UI3[Web UI]
    end
    
    subgraph "Core Engine"
        CE1[Code Reviewer]
        CE2[Agent Manager]
        CE3[Task Executor]
    end
    
    subgraph "Utilities"
        UT1[Git Utils]
        UT2[Bitbucket Utils]
        UT3[Bedrock Client]
    end
    
    subgraph "Configuration"
        CF1[Standards Loader]
        CF2[Guidelines Parser]
        CF3[Environment Config]
    end
    
    subgraph "External Systems"
        EX1[Local Git Repo]
        EX2[Bitbucket Server]
        EX3[AWS Bedrock]
    end
    
    UI1 --> CE1
    UI2 --> CE1
    UI3 --> CE1
    
    CE1 --> CE2
    CE1 --> CE3
    CE1 --> CF1
    CE1 --> CF2
    CE1 --> CF3
    
    CE1 --> UT1
    CE1 --> UT2
    CE1 --> UT3
    
    UT1 --> EX1
    UT2 --> EX2
    UT3 --> EX3
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Process File] --> B{File Readable?}
    B -->|No| C[Log Error & Skip]
    B -->|Yes| D[Extract Content]
    
    D --> E{Content Valid?}
    E -->|No| F[Use Diff Only]
    E -->|Yes| G[Build Context]
    
    F --> G
    G --> H[Send to AI]
    
    H --> I{AI Response OK?}
    I -->|No| J[Retry with Backoff]
    I -->|Yes| K[Parse Response]
    
    J --> L{Max Retries?}
    L -->|Yes| M[Log Failure & Continue]
    L -->|No| H
    
    K --> N{Valid JSON?}
    N -->|No| O[Attempt Repair]
    N -->|Yes| P[Process Result]
    
    O --> Q{Repair Success?}
    Q -->|No| M
    Q -->|Yes| P
    
    C --> R[Next File]
    M --> R
    P --> R
```

## Security Flow

```mermaid
flowchart LR
    subgraph "Authentication"
        A1[Environment Variables]
        A2[Token Validation]
        A3[Service Authentication]
    end
    
    subgraph "Data Protection"
        B1[Input Sanitization]
        B2[Secure Transmission]
        B3[Memory-Only Processing]
    end
    
    subgraph "Access Control"
        C1[Repository Access]
        C2[API Permissions]
        C3[Resource Limits]
    end
    
    A1 --> A2 --> A3
    A3 --> B1 --> B2 --> B3
    B3 --> C1 --> C2 --> C3
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        D1[Local CLI]
        D2[Python Environment]
        D3[Configuration Files]
    end
    
    subgraph "Production"
        P1[Docker Container]
        P2[FastAPI Server]
        P3[Nginx Proxy]
    end
    
    subgraph "CI/CD Integration"
        CI1[Git Hooks]
        CI2[Pipeline Trigger]
        CI3[Automated Review]
    end
    
    subgraph "External Services"
        E1[Bitbucket Server]
        E2[AWS Bedrock]
        E3[Monitoring Systems]
    end
    
    D1 --> D2 --> D3
    P1 --> P2 --> P3
    CI1 --> CI2 --> CI3
    
    D2 --> E1
    P2 --> E1
    CI3 --> E1
    
    D2 --> E2
    P2 --> E2
    CI3 --> E2
    
    P2 --> E3
```

## Performance Optimization Flow

```mermaid
flowchart TD
    A[Review Request] --> B[Load Configuration]
    B --> C{Cache Hit?}
    C -->|Yes| D[Use Cached Standards]
    C -->|No| E[Load from Files]
    
    D --> F[Process Files]
    E --> F
    
    F --> G{Parallel Processing?}
    G -->|Yes| H[Concurrent File Processing]
    G -->|No| I[Sequential Processing]
    
    H --> J[Aggregate Results]
    I --> J
    
    J --> K{Response Caching?}
    K -->|Yes| L[Cache AI Responses]
    K -->|No| M[Return Results]
    
    L --> M
    
    M --> N[Performance Metrics]
    N --> O[Optimization Feedback]
```

## Monitoring and Observability

```mermaid
graph LR
    subgraph "Metrics Collection"
        M1[Processing Time]
        M2[API Response Times]
        M3[Error Rates]
        M4[Resource Usage]
    end
    
    subgraph "Logging"
        L1[Structured Logs]
        L2[Error Tracking]
        L3[Performance Logs]
        L4[Audit Trail]
    end
    
    subgraph "Health Monitoring"
        H1[Service Health]
        H2[Dependency Status]
        H3[Resource Monitoring]
        H4[Alert System]
    end
    
    subgraph "Analytics"
        A1[Usage Patterns]
        A2[Review Quality]
        A3[Performance Trends]
        A4[User Behavior]
    end
    
    M1 --> L1
    M2 --> L2
    M3 --> L3
    M4 --> L4
    
    L1 --> H1
    L2 --> H2
    L3 --> H3
    L4 --> H4
    
    H1 --> A1
    H2 --> A2
    H3 --> A3
    H4 --> A4
```
