# 6. Architectural Design

Architectural design is a visual representation in software engineering that outlines the high-level structure and organization of a software system. It focuses on defining the major components or modules of the system, their interactions, and the overall system's architecture.

## 6.1 Architectural Context Diagram

At the architectural design level, a software architect uses an architectural context diagram (ACD) to model how software interacts with entities external to its boundaries. Systems that interoperate with the target system are represented as:

- **Superordinate systems** — Those systems that use the target system as part of some higher-level processing scheme.
- **Subordinate systems** — Those systems that are used by the target system and provide data or processing that are necessary to complete target system functionality.
- **Peer-level systems** — Those systems that interact on a peer-to-peer basis (i.e., information is either produced or consumed by the peers and the target system)
- **Actors** — Entities (people, devices) that interact with the target system by producing or consuming information that is necessary for requisite processing.

Each of these external entities communicates with the target system through an interface. Representation of MITRE ATT&CK Log Analysis System in Architectural Context Diagram is delineated as follows:

- **Superordinate systems** - Our system does not have any superordinate system (it operates as a standalone threat detection platform).
- **Subordinate systems** - Our system uses the Fine-tuned LLM for threat detection and technique extraction, MITRE ATT&CK Database for technique validation, and Log Sources (Windows Events, Sysmon, Network Traffic, Browser Logs) as data providers.
- **Peer-level systems** - Our system does not have any peer-level system.
- **Actors** - Security Analysts, SOC Teams, and Incident Responders are the core users of this system.

The architectural context diagram for the system is given below:

```mermaid
graph TB
    Actor["👤 Security Analyst"]

    subgraph System["MITRE ATT&CK Log Analysis System"]
        Core["Core Analysis Engine"]
    end

    subgraph Subordinate["Subordinate Systems"]
        LLM["Fine-tuned LLM<br/>Qwen2.5-1.5B-Instruct"]
        MITRE["MITRE ATT&CK<br/>Database"]
        Logs["Log Sources<br/>Windows, Sysmon,<br/>Network, Browser"]
    end

    Actor -->|"Initiates Analysis"| Core
    Core -->|"Delivers Reports"| Actor

    Core -->|"uses"| LLM
    Core -->|"uses"| MITRE
    Core -->|"uses"| Logs

    style Actor fill:#FFB3BA,stroke:#333,stroke-width:3px
    style Core fill:#B3D9FF,stroke:#1976D2,stroke-width:4px
    style LLM fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style MITRE fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style Logs fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
```

**Figure 6:** Architectural Context Diagram

---

## 6.2 Archetypes

The archetypes for the system are defined below:

```mermaid
graph TB
    subgraph DataCollection["Data Collection Pipeline"]
        DC1["Activate Log<br/>Collection Agents"]
        DC2["Monitor<br/>Target Systems"]
        DC3["Collect Multi-Source<br/>Logs"]
        DC4["Upload to<br/>Storage"]

        DC1 --> DC2 --> DC3 --> DC4
    end

    subgraph DataProcessing["Data Processing Pipeline"]
        DP1["Parse Raw Logs"]
        DP2["Remove Duplicates<br/>and Normalize"]
        DP3["Create 7-Log<br/>Chunks"]
        DP4["Anonymize PII"]

        DP1 --> DP2 --> DP3 --> DP4
    end

    subgraph Analysis["Threat Analysis Engine"]
        A1["Generate<br/>Embeddings"]
        A2["Additional Context<br/>Session Metadata"]
        A3["Classify Activity<br/>LLM Inference"]
        A4["Extract MITRE<br/>Techniques LLM"]

        A1 --> A3
        A2 --> A3
        A3 --> A4
    end

    subgraph Reporting["Report Generation"]
        R1["Compile Threat<br/>Data"]
        R2["Format Timeline<br/>and Evidence"]
        R3["Generate<br/>Recommendations"]
        R4["Export Report<br/>JSON PDF TXT"]

        R1 --> R2 --> R3 --> R4
    end

    Client["Security Analyst<br/>Workstation"]
    Server["Analysis Server"]
    Storage["Log Storage<br/>Database"]
    LLMServ["LLM Inference<br/>Server"]
    MITREDb["MITRE ATT&CK<br/>Database"]

    Client -->|"Request Analysis"| Server
    Server -->|"Deliver Report"| Client

    DataCollection --> Storage
    Storage --> DataProcessing
    DataProcessing --> Analysis
    Analysis --> Reporting
    Reporting --> Client

    Analysis -.->|"Inference Requests"| LLMServ
    Analysis -.->|"Query Techniques"| MITREDb

    style DataCollection fill:#FFE6B3,stroke:#F57C00,stroke-width:2px
    style DataProcessing fill:#FFF9C4,stroke:#F9A825,stroke-width:2px
    style Analysis fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style Reporting fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px
    style Client fill:#FFB3BA,stroke:#333,stroke-width:2px
    style Server fill:#B3D9FF,stroke:#1976D2,stroke-width:2px
    style Storage fill:#E0E0E0,stroke:#616161,stroke-width:2px
    style LLMServ fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style MITREDb fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
```

**Figure 7:** Archetypes

---

This **pipeline-based architecture** is tailored to balance real-time detection with comprehensive threat analysis. The Data Collection and Processing layers ensure that raw logs are transformed into structured, analyzable datasets. The Analysis Engine offloads computationally intensive tasks like LLM inference and MITRE technique extraction to dedicated servers, making the system scalable while maintaining high accuracy. The Reporting layer delivers actionable intelligence to security analysts in human-readable formats.

### Data Collection Pipeline

- **Activate Log Collection Agents:**

  - Deploys automated agents on target systems (Windows, Linux, network devices).
  - Acts as the initial stage to capture security-relevant events in real-time.
  - Ensures comprehensive coverage without impacting system performance.

- **Monitor Target Systems:**

  - Continuously monitors Windows Event Logs, Sysmon, network traffic, and browser activity.
  - Prepares the environment for real-time log streaming.

- **Collect Multi-Source Logs:**

  - Gathers logs from diverse sources (system logs, process execution, network packets, browser history).
  - Efficiently captures all security-relevant events with timestamps.

- **Upload to Storage:**
  - Securely uploads collected logs to cloud storage (Google Drive) or local database.
  - Ensures data integrity and backup for forensic analysis.

---

### Data Processing Pipeline

- **Parse Raw Logs:**

  - Converts heterogeneous log formats (XML, CSV, JSON, binary) into unified JSON structure.
  - Normalizes field names and data types for consistency.

- **Remove Duplicates & Normalize:**

  - Filters out duplicate log entries and system noise.
  - Normalizes timestamps to a consistent format (UTC).

- **Create 7-Log Chunks:**

  - Organizes logs into temporal segments of 7 consecutive events.
  - Optimizes for ML model input (approximately 2,200 tokens per chunk).

- **Anonymize PII:**
  - Strips personally identifiable information (usernames hashed, internal IPs masked).
  - Ensures privacy compliance while preserving forensic value.

---

### Threat Analysis Engine

- **Generate Embeddings:**

  - Converts text-based log chunks into numerical vector representations.
  - Prepares data for machine learning classification.

- **Additional Context (Session Metadata):**

  - Enriches log data with session information (start time, duration, system profile).
  - Provides contextual awareness for more accurate threat detection.

- **Classify Activity (LLM Inference):**

  - Uses the fine-tuned Qwen2.5-1.5B-Instruct model to classify sessions as Normal or Suspicious.
  - Leverages advanced pattern recognition to identify subtle attack indicators.

- **Extract MITRE Techniques (LLM):**
  - For suspicious sessions, extracts specific MITRE ATT&CK technique IDs (e.g., T1059.001, T1547.001).
  - Maps detected behaviors to standardized threat intelligence.

---

### Report Generation

- **Compile Threat Data:**

  - Aggregates classification results, extracted techniques, and session metadata.
  - Prepares comprehensive threat intelligence for reporting.

- **Format Timeline & Evidence:**

  - Constructs chronological attack timeline with precise timestamps.
  - Compiles relevant log excerpts as evidence.

- **Generate Recommendations:**

  - Provides actionable incident response steps (isolate system, investigate lateral movement, etc.).
  - Calculates risk scores based on detected techniques and confidence levels.

- **Export Report (JSON/PDF/TXT):**
  - Exports reports in multiple formats for different audiences.
  - JSON for machine-readable integration, PDF/TXT for human analysis.

---

## 6.3 Top Level Components

The overall architectural structure with top-level components is illustrated below:

```mermaid
graph TB
    subgraph UI["User Interface Layer"]
        Analyst["Security Analyst<br/>Dashboard"]
    end

    subgraph Application["Application Layer"]
        Controller["Analysis Controller"]
        SessionMgr["Session Manager"]
        ReportGen["Report Generator"]
    end

    subgraph Processing["Processing Layer"]
        LogCollector["Log Collector"]
        Preprocessor["Data Preprocessor"]
        Detector["Threat Detection<br/>Controller"]
        Mapper["MITRE Mapper"]
    end

    subgraph Integration["Integration Layer"]
        LLMInterface["Fine-tuned LLM<br/>Interface"]
        MITREInterface["MITRE Database<br/>Interface"]
    end

    subgraph Data["Data Layer"]
        LogDB["Log Database<br/>Raw and Clean Logs"]
        SessionDB["Session Store<br/>Analysis Results"]
    end

    subgraph External["External Systems"]
        LLMServer["LLM Server<br/>Qwen2.5-1.5B"]
        MITREServer["MITRE ATT&CK<br/>Knowledge Base"]
        LogSources["Log Sources<br/>Windows, Sysmon,<br/>Network, Browser"]
    end

    Analyst -->|"Request Analysis"| Controller
    Controller --> SessionMgr
    SessionMgr --> Detector
    Detector --> Mapper
    Mapper --> ReportGen
    ReportGen -->|"Deliver Report"| Analyst

    LogCollector -->|"Collect Logs"| LogSources
    LogCollector -->|"Store Raw Logs"| LogDB
    Preprocessor -->|"Read Raw Logs"| LogDB
    Preprocessor -->|"Store Clean Logs"| LogDB
    Preprocessor --> SessionMgr

    SessionMgr -->|"Retrieve Logs"| LogDB
    SessionMgr -->|"Store Results"| SessionDB

    Detector --> LLMInterface
    Mapper --> LLMInterface
    Mapper --> MITREInterface

    LLMInterface -->|"Inference Requests"| LLMServer
    MITREInterface -->|"Query Techniques"| MITREServer

    style Analyst fill:#FFB3BA,stroke:#333,stroke-width:3px
    style Controller fill:#B3D9FF,stroke:#1976D2,stroke-width:2px
    style SessionMgr fill:#B3D9FF,stroke:#1976D2,stroke-width:2px
    style ReportGen fill:#E1BEE7,stroke:#6A1B9A,stroke-width:2px
    style LogCollector fill:#FFE6B3,stroke:#F57C00,stroke-width:2px
    style Preprocessor fill:#FFF9C4,stroke:#F9A825,stroke-width:2px
    style Detector fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style Mapper fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style LLMInterface fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style MITREInterface fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    style LogDB fill:#E0E0E0,stroke:#616161,stroke-width:2px
    style SessionDB fill:#E0E0E0,stroke:#616161,stroke-width:2px
    style LLMServer fill:#FFCCBC,stroke:#D84315,stroke-width:2px
    style MITREServer fill:#FFCCBC,stroke:#D84315,stroke-width:2px
    style LogSources fill:#FFCCBC,stroke:#D84315,stroke-width:2px
```

**Figure 8:** Top Level Components

---

## 6.4 Mapping Requirements to Software Architecture

The mapping of the derived components with the requirements can be shown below:

| **Requirements**                           | **Components**                                                                                            |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| **Automated Log Collection**               | Activate Log Collection Agents, Monitor Target Systems, Collect Multi-Source Logs, Upload to Storage      |
| **Good Detection Accuracy**                | Generate Embeddings, Classify Activity (LLM Inference), Calculate Confidence, Threat Detection Controller |
| **MITRE ATT&CK Mapping**                   | Extract MITRE Techniques (LLM), MITRE Mapper, MITRE Database Interface, Query Techniques                  |
| **Timestamped Event Logs**                 | Collect Multi-Source Logs, Parse Raw Logs, Normalize Timestamps, Format Timeline & Evidence               |
| **Privacy Protection**                     | Anonymize PII, Data Preprocessor, Secure Storage                                                          |
| **Context-Aware Detection**                | Additional Context (Session Metadata), Session Manager, Retrieve Contextual Data                          |
| **Detailed Threat Explanations**           | Generate Recommendations, Compile Threat Data, Report Generator, Export Report                            |
| **Fast Processing Speed**                  | Create 7-Log Chunks, Batch Inference, LLM Interface, Parallel Processing                                  |
| **Comprehensive Reporting**                | Format Timeline & Evidence, Compile Threat Data, Generate Recommendations, Export Report (JSON/PDF/TXT)   |
| **Multi-Source Log Integration**           | Log Collector, Parse Raw Logs, Remove Duplicates & Normalize, Log Database                                |
| **Fine-Tuned Language Model**              | Fine-tuned LLM Interface, LLM Server (Qwen2.5-1.5B), Generate Embeddings, Classify Activity               |
| **Automated MITRE Technique Extraction**   | Extract MITRE Techniques (LLM), MITRE Mapper, Validate Techniques                                         |
| **Explainable AI with Reasoning**          | Generate Recommendations, Compile Threat Data, Format Timeline & Evidence                                 |
| **Multi-Stage Attack Pattern Recognition** | Session Manager, Create 7-Log Chunks, Classify Activity, Extract MITRE Techniques                         |
| **Session-Based Analysis**                 | Session Manager, Create Session, Assign Chunks, Update Session Status                                     |

---

## Conclusion

In the current report, I have detailed all the necessary technical specifications required to develop the MITRE ATT&CK Log Analysis System: an intelligent threat detection platform designed to automate the analysis of system, process, and network logs. I have elaborated on the project scope, requirements, and usage scenarios in detail. Scenario-based modeling and class-based modeling were conducted to establish a resilient system architecture. In addition, the architectural design has been presented to illustrate the high-level structure and component interactions.

While the MITRE ATT&CK Log Analysis System can effectively detect and explain suspicious activities by leveraging advanced machine learning and the MITRE framework, there is always room for improvement. Future enhancements could include: supporting additional log sources (cloud platforms like AWS CloudTrail, Azure Monitor), integrating with SIEM platforms for real-time alerting, expanding technique coverage to include emerging threats, and incorporating user feedback mechanisms to continuously refine the detection model.

This document should provide a comprehensive understanding of the workflow, technical design, and architectural structure of this system. I hope it will serve as a valuable resource for understanding the MITRE ATT&CK Log Analysis System and its development process.

---

**End of Architectural Design Section**
