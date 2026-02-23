# Section 7: Preliminary Test Plan

In this chapter, a high-level description of testing goals and a summary of features to be tested are presented.

---

## 7.1 High-Level Description of Testing Goals

Testing goals for this system are represented below from a high level:

- **To verify that the MITRE ATT&CK Log Analysis System meets its most important functional and non-functional requirements.**
- **To ensure log collection from multiple sources (Sysmon, network traffic, browser logs) is accurate and complete.**
- **To validate that data preprocessing correctly cleans, normalizes, and structures raw logs for analysis.**
- **To confirm that threat detection identifies suspicious activity with high accuracy and minimal false positives.**
- **To ensure MITRE ATT&CK technique mapping is correct and corresponds to actual attack behaviors in logs.**
- **To verify that the fine-tuned LLM generates accurate classifications, technique extractions, and explanations.**
- **To test that threat reports are comprehensive, well-formatted, and contain actionable recommendations.**
- **To validate session management correctly tracks user sessions and maintains analysis state.**
- **To ensure the system handles large volumes of logs efficiently without performance degradation.**
- **To confirm seamless integration with external systems (MITRE ATT&CK database, Google Drive, log sources).**

---

## 7.2 Test Cases

Test cases for the testing of this system are documented below:

### Test Case T1

| **Test Case Id**     | T1                                                                                                                                                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | Log Collection and Parsing                                                                                                                                                                                              |
| **Test Scenario**    | - Configure log sources (Sysmon, Wireshark PCAP, browser logs).<br>- Collect logs from a Windows system running normal and suspicious activities.<br>- Verify that all log types are successfully collected and parsed. |
| **Expected Outcome** | - All log sources are successfully connected.<br>- Logs are collected without data loss.<br>- Parsed logs contain all required fields (timestamp, event_id, process_name, network_src_ip, etc.).                        |

---

### Test Case T2

| **Test Case Id**     | T2                                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Title**            | Data Preprocessing and Cleaning                                                                                                                                                                                    |
| **Test Scenario**    | - Input raw logs containing duplicates, missing fields, and inconsistent formats.<br>- Run the data preprocessing module.<br>- Verify that logs are cleaned, normalized, and structured correctly.                 |
| **Expected Outcome** | - Duplicate logs are removed.<br>- Missing fields are handled appropriately (filled with defaults or flagged).<br>- Timestamps are normalized to ISO 8601 format.<br>- JSON structure matches the expected schema. |

---

### Test Case T3

| **Test Case Id**     | T3                                                                                                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Title**            | Threat Detection Accuracy                                                                                                                                                                                                            |
| **Test Scenario**    | - Process a dataset containing 7 logs from a known attack scenario (e.g., credential dumping with Mimikatz).<br>- Run the threat detection controller.<br>- Verify that the system correctly classifies the session as "Suspicious". |
| **Expected Outcome** | - The session is classified as "Suspicious" with high confidence (>0.85).<br>- Suspicious events are correctly identified (e.g., lsass.exe memory access).<br>- No false negatives (attack is not missed).                           |

---

### Test Case T4

| **Test Case Id**     | T4                                                                                                                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | MITRE ATT&CK Technique Mapping                                                                                                                                                           |
| **Test Scenario**    | - Analyze logs from a credential dumping attack.<br>- Request MITRE technique extraction from the system.<br>- Verify that the correct technique is mapped (T1003.001 - LSASS Memory).   |
| **Expected Outcome** | - The system accurately identifies technique T1003.001.<br>- The technique description matches MITRE ATT&CK documentation.<br>- Related sub-techniques are also suggested if applicable. |

---

### Test Case T5

| **Test Case Id**     | T5                                                                                                                                                                                                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | Fine-Tuned LLM Integration                                                                                                                                                                                                                                                   |
| **Test Scenario**    | - Provide 7 preprocessed logs to the fine-tuned LLM interface.<br>- Request classification, technique extraction, explanation, and recommendations.<br>- Validate the LLM response structure and content quality.                                                            |
| **Expected Outcome** | - LLM returns a well-formatted JSON response.<br>- Classification is correct ("Normal" or "Suspicious").<br>- MITRE techniques are accurate and relevant.<br>- Explanation is clear and references specific log events.<br>- Recommendations are actionable and appropriate. |

---

### Test Case T6

| **Test Case Id**     | T6                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | Report Generation                                                                                                                                                                                                                                                                                                                                                             |
| **Test Scenario**    | - Complete a threat analysis on a suspicious session.<br>- Generate a threat report using the ReportGenerator class.<br>- Verify report completeness and format.                                                                                                                                                                                                              |
| **Expected Outcome** | - Report contains all required sections:<br>&nbsp;&nbsp;- Session summary (timestamps, classification, confidence)<br>&nbsp;&nbsp;- MITRE techniques with descriptions<br>&nbsp;&nbsp;- Detailed explanation with log references<br>&nbsp;&nbsp;- Actionable recommendations<br>- Report is formatted correctly (Markdown/PDF).<br>- Report is saved to the correct location. |

---

### Test Case T7

| **Test Case Id**     | T7                                                                                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Title**            | Session Management                                                                                                                                                                                                                                                 |
| **Test Scenario**    | - Create multiple analysis sessions (3 normal, 2 suspicious).<br>- Store session metadata using the SessionManager class.<br>- Retrieve session history and verify data persistence.                                                                               |
| **Expected Outcome** | - All sessions are successfully created with unique IDs.<br>- Session metadata (classification, timestamps, log count) is stored correctly.<br>- Session retrieval returns accurate historical data.<br>- Sessions can be queried by date range or classification. |

---

### Test Case T8

| **Test Case Id**     | T8                                                                                                                                                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | Handling Large Log Volumes                                                                                                                                                                                                                          |
| **Test Scenario**    | - Process a dataset containing 10,000+ log entries (1,400+ sessions).<br>- Measure system performance (processing time, memory usage).<br>- Verify that all sessions are analyzed without errors.                                                   |
| **Expected Outcome** | - System processes all sessions successfully.<br>- Processing time is reasonable (< 5 seconds per 7-log session on standard hardware).<br>- Memory usage remains stable (no memory leaks).<br>- Results accuracy is maintained across all sessions. |

---

### Test Case T9

| **Test Case Id**     | T9                                                                                                                                                                                                                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | Integration with MITRE ATT&CK Database                                                                                                                                                                                                                                                                                                                  |
| **Test Scenario**    | - Query the MITRE ATT&CK database for technique details (e.g., T1003.001).<br>- Verify that the system retrieves correct technique information.<br>- Test with multiple techniques from different tactics.                                                                                                                                              |
| **Expected Outcome** | - Technique information is retrieved successfully.<br>- Retrieved data includes:<br>&nbsp;&nbsp;- Technique ID and name<br>&nbsp;&nbsp;- Tactic(s) associated<br>&nbsp;&nbsp;- Description and detection methods<br>- Queries complete within acceptable time (< 2 seconds).<br>- System handles missing techniques gracefully (returns error message). |

---

### Test Case T10

| **Test Case Id**     | T10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Title**            | End-to-End System Integration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **Test Scenario**    | - Execute complete workflow from log collection to report generation:<br>&nbsp;&nbsp;1. Collect raw logs from test environment<br>&nbsp;&nbsp;2. Preprocess and clean logs<br>&nbsp;&nbsp;3. Detect suspicious activity<br>&nbsp;&nbsp;4. Map MITRE techniques<br>&nbsp;&nbsp;5. Generate threat report<br>- Verify that all components work together seamlessly.                                                                                                                                                                               |
| **Expected Outcome** | - Complete workflow executes without errors.<br>- Data flows correctly between all components:<br>&nbsp;&nbsp;- LogCollector → DataPreprocessor<br>&nbsp;&nbsp;- DataPreprocessor → ThreatDetectionController<br>&nbsp;&nbsp;- ThreatDetectionController → FineTunedLLMInterface<br>&nbsp;&nbsp;- FineTunedLLMInterface → MITREMapper<br>&nbsp;&nbsp;- All results → ReportGenerator<br>- Final report accurately reflects the analyzed session.<br>- Total end-to-end processing time is acceptable (< 30 seconds for a single 7-log session). |

---

## 7.3 Test Environment

### Hardware Requirements

- **Processor**: Intel Core i5 or equivalent (minimum), Intel Core i7 or AMD Ryzen 7 (recommended)
- **Memory**: 8 GB RAM (minimum), 16 GB RAM (recommended)
- **Storage**: 500 GB available disk space (for log storage and model files)
- **GPU**: NVIDIA GPU with 8+ GB VRAM (optional, for faster LLM inference)

### Software Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: Version 3.10 or higher
- **Dependencies**:
  - transformers >= 4.36.0
  - torch >= 2.0.0
  - datasets >= 2.14.0
  - peft >= 0.7.0
  - pandas >= 2.0.0
  - numpy >= 1.24.0
- **Log Sources**:
  - Sysmon (v15.0 or later) installed on test Windows system
  - Wireshark for PCAP capture
  - Browser logging extensions (Chrome/Firefox)

### Test Data

- **Normal Activity Dataset**: 5,000 log entries from benign user sessions (web browsing, file operations, system updates)
- **Suspicious Activity Dataset**: 3,000 log entries from simulated attacks:
  - Credential dumping (Mimikatz)
  - Data exfiltration (Google Drive, Dropbox)
  - Persistence mechanisms (Registry modification, Scheduled Tasks)
  - Lateral movement attempts
  - Reconnaissance activities
- **MITRE ATT&CK Reference Data**: Offline copy of MITRE ATT&CK Enterprise matrix (latest version)

---

## 7.4 Test Metrics

The following metrics will be collected during testing to evaluate system performance:

| **Metric**                    | **Description**                                                                          | **Target Value** |
| ----------------------------- | ---------------------------------------------------------------------------------------- | ---------------- |
| **Classification Accuracy**   | Percentage of sessions correctly classified as Normal or Suspicious                      | ≥ 85%            |
| **MITRE Technique Precision** | Percentage of extracted techniques that are correct                                      | ≥ 80%            |
| **MITRE Technique Recall**    | Percentage of actual techniques present in logs that are detected                        | ≥ 75%            |
| **False Positive Rate**       | Percentage of normal sessions incorrectly classified as suspicious                       | ≤ 10%            |
| **False Negative Rate**       | Percentage of suspicious sessions incorrectly classified as normal                       | ≤ 8%             |
| **Processing Time**           | Average time to analyze a 7-log session                                                  | ≤ 5 seconds      |
| **Report Generation Time**    | Average time to generate a complete threat report                                        | ≤ 10 seconds     |
| **System Uptime**             | Percentage of time system is operational during testing                                  | ≥ 99%            |
| **Memory Usage**              | Peak memory consumption during analysis                                                  | ≤ 8 GB           |
| **LLM Response Quality**      | Average quality score for explanations and recommendations (1-10 scale, human-evaluated) | ≥ 7.5            |

---

## 7.5 Testing Schedule

| **Phase**                   | **Duration** | **Activities**                                                                                                                                                        |
| --------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Unit Testing**            | 2 weeks      | - Test individual classes (LogCollector, DataPreprocessor, etc.)<br>- Verify each module's core functionality<br>- Fix bugs and refine implementations                |
| **Integration Testing**     | 2 weeks      | - Test interactions between components<br>- Verify data flow through the complete pipeline<br>- Test end-to-end scenarios (T10)                                       |
| **Performance Testing**     | 1 week       | - Test with large datasets (T8)<br>- Measure processing times and resource usage<br>- Optimize bottlenecks                                                            |
| **Accuracy Testing**        | 2 weeks      | - Evaluate classification accuracy (T3)<br>- Validate MITRE technique mapping (T4)<br>- Test with diverse attack scenarios<br>- Calculate precision, recall, F1-score |
| **User Acceptance Testing** | 1 week       | - Deploy to test users (security analysts)<br>- Collect feedback on report quality and usability<br>- Validate that system meets user requirements                    |
| **Regression Testing**      | Ongoing      | - Re-run critical test cases after each code change<br>- Ensure new features don't break existing functionality                                                       |

**Total Testing Duration**: 8 weeks (excluding ongoing regression testing)

---

## 7.6 Success Criteria

The system will be considered ready for deployment if:

1. **All 10 test cases (T1-T10) pass successfully** with expected outcomes achieved.
2. **Classification accuracy ≥ 85%** on the test dataset.
3. **MITRE technique precision ≥ 80%** and recall ≥ 75%.
4. **False positive rate ≤ 10%** and false negative rate ≤ 8%.
5. **Performance targets met**: Processing time ≤ 5 seconds per session, report generation ≤ 10 seconds.
6. **No critical bugs** (system crashes, data loss, incorrect classifications on known attacks).
7. **User acceptance testing** shows positive feedback from at least 80% of test users.
8. **Documentation is complete**: User manual, API documentation, deployment guide.

---

## 7.7 Risk Assessment

| **Risk**                                    | **Probability** | **Impact** | **Mitigation Strategy**                                                                                              |
| ------------------------------------------- | --------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| **LLM generates incorrect techniques**      | Medium          | High       | - Implement validation against MITRE database<br>- Provide confidence scores<br>- Allow manual correction in reports |
| **High false positive rate**                | Medium          | Medium     | - Fine-tune detection thresholds<br>- Improve training data quality<br>- Implement multi-stage verification          |
| **Performance degradation with large logs** | Low             | Medium     | - Optimize data processing pipeline<br>- Implement batch processing<br>- Use efficient data structures               |
| **Integration issues with log sources**     | Low             | High       | - Test with multiple log formats<br>- Implement robust error handling<br>- Provide clear error messages              |
| **Model overfitting to training scenarios** | Medium          | High       | - Use diverse training data<br>- Implement regularization techniques<br>- Test on unseen attack scenarios            |

---

## 7.8 Conclusion

This preliminary test plan provides a structured approach to validating the MITRE ATT&CK Log Analysis System. By systematically testing each component and the integrated system, we ensure that the tool meets its functional and non-functional requirements, delivers accurate threat detection, and provides actionable intelligence to security analysts.

The test cases cover critical functionality including log collection, data preprocessing, threat detection, MITRE technique mapping, LLM integration, report generation, and system performance. Success metrics are clearly defined, and risks are identified with appropriate mitigation strategies.

Upon successful completion of all testing phases and meeting the defined success criteria, the system will be ready for deployment in production security operations environments.
