from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Domain Enums / Literal Types
IncidentStatus = Literal[
    'open',
    'investigating',
    'diagnosed',
    'pending_approval',
    'executing',
    'verifying',
    'resolved',
    'escalated'
]

AgentType = Literal[
    'triage',
    'investigation',
    'diagnosis',
    'action_planner',
    'verification'
]

EvidenceType = Literal[
    'knowledge_base',
    'ticket',
    'system_status',
    'procedure'
]

RiskLevel = Literal['low', 'medium', 'high', 'critical']

PriorityLevel = Literal['low', 'medium', 'high', 'critical']

# Evidence Model
class Evidence(BaseModel):
    id: str
    type: EvidenceType
    title: str
    content: str
    relevance: int = Field(ge=0, le=100) # 0-100
    source: Optional[str] = None

# Diagnosis Model
class Diagnosis(BaseModel):
    likelyCause: str
    confidence: int = Field(ge=0, le=100) # 0-100
    supportingEvidence: List[Evidence] = Field(default_factory=list)
    uncertainty: Optional[str] = None

# Action Model
class Action(BaseModel):
    id: str
    tool: str
    description: str
    riskLevel: RiskLevel
    requiresApproval: bool
    linkedEvidence: List[Evidence] = Field(default_factory=list)
    reasoning: str

# Agent Event Model
class AgentEvent(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=get_utc_now)
    agent: AgentType
    status: Literal['started', 'processing', 'completed', 'failed']
    message: str
    evidence: Optional[List[Evidence]] = None
    diagnosis: Optional[Diagnosis] = None
    action: Optional[Action] = None

# Resolution Model
class IncidentResolution(BaseModel):
    timestamp: datetime = Field(default_factory=get_utc_now)
    verificationMethod: str
    success: bool

# Incident Model
class Incident(BaseModel):
    id: str
    title: str
    description: str
    status: IncidentStatus = 'open'
    createdAt: datetime = Field(default_factory=get_utc_now)
    updatedAt: datetime = Field(default_factory=get_utc_now)
    priority: PriorityLevel = 'medium'
    category: str = 'General IT'
    events: List[AgentEvent] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    diagnosis: Optional[Diagnosis] = None
    proposedAction: Optional[Action] = None
    approvalRequired: bool = False
    escalationReason: Optional[str] = None
    resolution: Optional[IncidentResolution] = None

# Request / Response Schemas
class IncidentCreateRequest(BaseModel):
    description: str
    title: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    category: Optional[str] = None
    user_id: Optional[str] = 'usr_default'

class ApprovalRequest(BaseModel):
    approved: bool
    operator_id: Optional[str] = 'admin'
    notes: Optional[str] = None

class DashboardMetrics(BaseModel):
    activeIncidents: int
    aiResolutions: int
    escalations: int
    avgResolutionTime: float
