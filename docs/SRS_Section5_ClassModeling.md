# 5. Class-Based Modeling

Class-based modeling is a visual representation in software engineering that illustrates the structure of a software system using classes, their attributes, and relationships. It is commonly used in object-oriented design and modeling.

## 5.1 Analysis Classes

After identifying nouns from the usage scenario and system architecture, I filtered nouns belonging to the solution domain using General Classification (External entities, Things, Events, Roles, Organizational units, Places, and Structures). Nouns selected as potential classes were filtered using Selection Criteria (Retained information, Needed services, Multiple attributes, Common attributes, Common operations, and Essential requirements). After performing analysis on potential classes, I have found the following analysis classes:

1. **LogCollector**
2. **DataPreprocessor**
3. **ThreatDetectionController**
4. **MITREMapper**
5. **ReportGenerator**
6. **FineTunedLLMInterface**
7. **SessionManager**
8. **LogDatabase**

---

## 5.2 Class Cards

### LogCollector

| **Attributes**                                                                                     | **Methods**                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - monitored_systems<br>- collection_interval<br>- log_sources<br>- storage_path<br>- active_agents | + start_collection()<br>+ stop_collection()<br>+ collect_system_logs()<br>+ collect_network_traffic()<br>+ collect_browser_logs()<br>+ upload_to_storage()<br>+ validate_log_integrity() |

| **Responsibilities**                                                                                                                    | **Collaborators**                   |
| --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Continuously monitor target systems and collect logs from multiple sources (Windows Events, Sysmon, network traffic, browser activity). | ● DataPreprocessor<br>● LogDatabase |

---

### DataPreprocessor

| **Attributes**                                                                           | **Methods**                                                                                                                                                   |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - raw_logs<br>- clean_logs<br>- chunk_size<br>- anonymization_rules<br>- schema_mappings | + parse_logs()<br>+ remove_duplicates()<br>+ normalize_timestamps()<br>+ anonymize_pii()<br>+ create_chunks()<br>+ validate_structure()<br>+ export_to_json() |

| **Responsibilities**                                                                                        | **Collaborators**                                   |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Transform raw, unstructured logs into clean, standardized JSON format organized into 7-log temporal chunks. | ● LogCollector<br>● LogDatabase<br>● SessionManager |

---

### ThreatDetectionController

| **Attributes**                                                                                                         | **Methods**                                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - detection_model<br>- confidence_threshold<br>- chunk_embeddings<br>- classification_results<br>- suspicious_sessions | + analyze_session()<br>+ generate_embeddings()<br>+ classify_activity()<br>+ calculate_confidence()<br>+ flag_suspicious()<br>+ update_detection_model() |

| **Responsibilities**                                                                                                                   | **Collaborators**                                            |
| -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Analyze preprocessed log chunks using the fine-tuned LLM to identify anomalous patterns and classify sessions as Normal or Suspicious. | ● FineTunedLLMInterface<br>● SessionManager<br>● MITREMapper |

---

### MITREMapper

| **Attributes**                                                                                              | **Methods**                                                                                                                                    |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| - mitre_database<br>- technique_catalog<br>- tactic_mappings<br>- extracted_techniques<br>- attack_timeline | + extract_techniques()<br>+ map_to_tactics()<br>+ query_mitre_db()<br>+ identify_iocs()<br>+ reconstruct_timeline()<br>+ validate_techniques() |

| **Responsibilities**                                                                                                      | **Collaborators**                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| For suspicious sessions, extract specific MITRE ATT&CK techniques, map them to tactics, and reconstruct attack timelines. | ● ThreatDetectionController<br>● FineTunedLLMInterface<br>● ReportGenerator |

---

### ReportGenerator

| **Attributes**                                                                              | **Methods**                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - report_template<br>- threat_data<br>- output_format<br>- report_metadata<br>- risk_levels | + create_executive_summary()<br>+ format_technique_list()<br>+ generate_timeline()<br>+ compile_evidence()<br>+ add_recommendations()<br>+ export_report()<br>+ calculate_risk_score() |

| **Responsibilities**                                                                                                                       | **Collaborators**                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Generate comprehensive, human-readable threat reports containing detected techniques, timelines, evidence, and actionable recommendations. | ● MITREMapper<br>● ThreatDetectionController<br>● SessionManager |

---

### FineTunedLLMInterface

| **Attributes**                                                                       | **Methods**                                                                                                                                  |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| - model_name<br>- tokenizer<br>- max_length<br>- model_weights<br>- inference_config | + load_model()<br>+ tokenize_input()<br>+ generate_prediction()<br>+ extract_techniques()<br>+ generate_explanation()<br>+ batch_inference() |

| **Responsibilities**                                                                                                       | **Collaborators**                            |
| -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Interface with the fine-tuned Qwen2.5-1.5B-Instruct model to perform threat classification and MITRE technique extraction. | ● ThreatDetectionController<br>● MITREMapper |

---

### SessionManager

| **Attributes**                                                                                  | **Methods**                                                                                                                                       |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| - active_sessions<br>- session_metadata<br>- chunk_mappings<br>- session_status<br>- timestamps | + create_session()<br>+ assign_chunks()<br>+ update_session_status()<br>+ get_session_data()<br>+ merge_related_sessions()<br>+ archive_session() |

| **Responsibilities**                                                                                                              | **Collaborators**                                                      |
| --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Organize logs into session-based analysis units, manage session lifecycle, and track analysis progress for each monitored period. | ● DataPreprocessor<br>● ThreatDetectionController<br>● ReportGenerator |

---

### LogDatabase

| **Attributes**                                                                                     | **Methods**                                                                                                                            |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| - raw_log_storage<br>- clean_log_storage<br>- index_mappings<br>- storage_quota<br>- backup_config | + store_raw_logs()<br>+ store_clean_logs()<br>+ query_logs()<br>+ retrieve_session_logs()<br>+ create_backup()<br>+ manage_retention() |

| **Responsibilities**                                                                                                         | **Collaborators**                                        |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Persist raw and processed logs with proper indexing, manage storage retention policies, and provide efficient log retrieval. | ● LogCollector<br>● DataPreprocessor<br>● SessionManager |

---

## 5.3 CRC Diagram

The CRC (Class-Responsibility-Collaboration) diagram illustrating the relationships between classes is shown below:

```mermaid
graph TB
    TDC[ThreatDetectionController]
    LC[LogCollector]
    DP[DataPreprocessor]
    SM[SessionManager]
    LLMI[FineTunedLLMInterface]
    MM[MITREMapper]
    RG[ReportGenerator]
    LDB[LogDatabase]

    LC -->|Provide Raw Logs| DP
    LC -->|Store Logs| LDB
    DP -->|Create Chunks| SM
    DP -->|Access Stored Logs| LDB
    SM -->|Provide Sessions<br/>for Analysis| TDC
    TDC -->|Request Inference| LLMI
    TDC -->|Send Suspicious<br/>Sessions| MM
    MM -->|Request Technique<br/>Extraction| LLMI
    MM -->|Provide Detected<br/>Techniques| RG
    SM -->|Provide Session<br/>Metadata| RG
    TDC -->|Provide<br/>Classifications| RG
    LDB -->|Retrieve Session<br/>Logs| SM

    style TDC fill:#FFE6B3,stroke:#333,stroke-width:2px
    style LC fill:#FFE6B3,stroke:#333,stroke-width:2px
    style DP fill:#FFE6B3,stroke:#333,stroke-width:2px
    style SM fill:#FFE6B3,stroke:#333,stroke-width:2px
    style LLMI fill:#FFE6B3,stroke:#333,stroke-width:2px
    style MM fill:#FFE6B3,stroke:#333,stroke-width:2px
    style RG fill:#FFE6B3,stroke:#333,stroke-width:2px
    style LDB fill:#FFE6B3,stroke:#333,stroke-width:2px
```

**Figure 8:** CRC Diagram of MITRE ATT&CK Log Analysis System

**End of Class-Based Modeling Section**
