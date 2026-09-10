from backend.app.schemas.battery import (
    BatteryCreate,
    BatteryResponse,
    BatteryStatus,
    BatteryWithInspectionsResponse,
)

from backend.app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse
)

from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    UserRole
)

from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from backend.app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
)
from backend.app.schemas.dashboard import (
    DashboardSummaryResponse,
    HealthTrendItem,
    RecentInspectionItem,
    CriticalBatteryItem,
)
from backend.app.schemas.attachment import AttachmentResponse