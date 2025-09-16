import {
  Target,
  Zap,
  Key,
  Gamepad,
  Lock,
  Upload,
  RefreshCw,
  Bomb,
  Trash2,
} from "lucide-react";

export const attackSteps = {
  initialAccess: [
    "Phishing email/message with mega link (direct exe download)",
    "Phishing email/message with mega link (direct zip download)",
    "Phishing email/message with mega link (direct rar download(without password))",
    "Phishing email/message with mega link (direct rar download(with password))",
    "Phishing email/message with mega link (bound to pdf)",
    "Phishing email/message with drive link (direct exe download)",
    "Phishing email/message with drive link (direct zip download)",
    "Phishing email/message with drive link (direct rar download(without password))",
    "Phishing email/message with drive link (direct rar download(with password))",
    "Phishing email/message with drive link (bound to pdf)",
    "Phishing whatsapp/message with drive link (direct exe download)",
    "Phishing whatsapp/message with drive link (direct zip download)",
    "Phishing whatsapp/message with drive link (direct rar download(without password))",
    "Phishing whatsapp/message with drive link (direct rar download(with password))",
    "Phishing whatsapp/message with drive link (bound to pdf)",
    "Phishing whatsapp/message with fake installer (game update)",
    "Phishing messenger/message with drive link (direct exe download)",
    "Phishing messenger/message with drive link (direct zip download)",
    "Phishing messenger/message with drive link (direct rar download(without password))",
    "Phishing messenger/message with drive link (direct rar download(with password))",
    "Phishing messenger/message with drive link (bound to pdf)",
    "Phishing telegram/message with drive link (direct exe download)",
    "Phishing telegram/message with drive link (direct zip download)",
    "Phishing telegram/message with drive link (direct rar download(without password))",
    "Phishing telegram/message with drive link (direct rar download(with password))",
    "Phishing telegram/message with drive link (bound to pdf)",
    "Phishing in telegram through direct exe download",
    "Phishing in telegram through direct zip download",
    "Phishing in telegram through direct rar download(without password)",
    "Phishing in telegram through direct rar download(with password)",
    "Phishing in telegram through link bound to image",
    "Phishing in telegram through link bound to pdf",
    "Payload from public GitHub repo by cloning (click exe directly)",
    "Payload from public GitHub repo by cloning (click to a pdf file)",
    "Payload from public GitHub repo by cloning (Run the project)",
    "Payload from public GitHub repo by downloading (click exe directly)",
    "Payload from public GitHub repo by downloading (click to a pdf file)",
    "Payload from public GitHub repo by downloading (Run the project)",
    "Watering hole attack on compromised website",
    "USB drop attack with malicious payload",
  ],
  operationAfterInitialAccess: ["Delete files", "Edit files"],
  credentialHarvesting: ["RAT + WebBrowserPassView credential extraction"],
  attackerControl: [
    "Immediate control after compromise (RAT activation)",
    "Delayed control after dormancy period (scheduled activation, trigger-based)",
  ],
  persistence: [
    "Bootloader-based payload persistence",
    "Task Scheduler payload persistence",
  ],
  dataExfiltration: [
    "USB exfiltration",
    "Google Drive exfiltration",
    "RAT server exfiltration",
    "OneDrive exfiltration",
    "GitHub exfiltration",
  ],
  finalPayload: [
    "Ransomware (using 7zip to compress files/folders before encryption)",
    "Ransomware (full disk encryption)",
  ],
  postAttackCleanup: ["Leaving traces", "Leaving no trace (stealth cleanup)"],
  lateralMovement: ["Windows SMB lateral movement", "Internal spear phishing"],
};

export const stepConfig = {
  initialAccess: {
    required: true,
    label: "Initial Access Vector",
    description: "How the attacker gains first access to the system",
  },
  operationAfterInitialAccess: {
    required: true,
    label: "Post-Breach Operations",
    description: "Immediate actions after gaining access",
    defaultIndex: 0,
  },
  credentialHarvesting: {
    required: true,
    label: "Credential Harvesting",
    description: "Methods to extract user credentials",
    defaultIndex: 0,
  },
  attackerControl: {
    required: true,
    label: "Command & Control",
    description: "How the attacker maintains control",
    defaultIndex: 0,
  },
  dataExfiltration: {
    required: true,
    label: "Data Exfiltration",
    description: "How sensitive data is stolen",
    defaultIndex: 0,
  },
  finalPayload: {
    required: true,
    label: "Final Impact",
    description: "The ultimate goal of the attack",
    defaultIndex: 0,
  },
  postAttackCleanup: {
    required: false,
    label: "Attack Cleanup",
    description: "How traces are handled",
  },
  lateralMovement: {
    required: false,
    label: "Lateral Movement",
    description: "Spreading to other systems",
  },
  persistence: {
    required: true,
    label: "Persistence Mechanism",
    description: "Methods to maintain access across reboots",
    defaultIndex: 0,
  },
};

export const priorityStepOrder = [
  "initialAccess",
  "operationAfterInitialAccess",
  "credentialHarvesting",
  "attackerControl",
  "dataExfiltration",
  "finalPayload",
  "postAttackCleanup",
  "persistence",
  "lateralMovement",
];

export const getStepIcon = (stepKey) => {
  const iconMap = {
    initialAccess: Target,
    operationAfterInitialAccess: Zap,
    credentialHarvesting: Key,
    attackerControl: Gamepad,
    persistence: Lock,
    dataExfiltration: Upload,
    lateralMovement: RefreshCw,
    finalPayload: Bomb,
    postAttackCleanup: Trash2,
  };
  return iconMap[stepKey] || Target;
};

export const getStepColor = (index) => {
  const colors = [
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "gray",
  ];
  return colors[index] || "gray";
};
