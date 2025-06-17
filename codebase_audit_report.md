# Pass Culture Codebase Audit Report

## Executive Summary

This audit examines the Pass Culture codebase, a French cultural platform that provides digital vouchers for cultural activities to young people. The codebase is organized as a monorepo containing multiple applications with a clear separation of concerns between backend API, frontend applications, and supporting infrastructure.

## Overall Architecture

### Repository Structure
The monorepo is organized into distinct modules:

```
pass-culture-main/
├── api/                    # Python Flask backend API
├── pro/                    # React frontend for cultural professionals
├── app-engine/            # Google App Engine related components
├── infra/                 # Infrastructure scripts and configurations
├── maintenance-site/      # Static maintenance page
├── nginx/                 # Nginx configuration
├── scripts/               # Various utility scripts
└── docker-compose files   # Container orchestration
```

### Technology Stack

**Backend (API)**
- **Framework**: Flask 2.0 (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis broker
- **API Documentation**: Spectree (OpenAPI)
- **Authentication**: Flask-Login, JWT, SAML2
- **Testing**: Pytest with extensive test coverage
- **Code Quality**: Ruff (linting), MyPy (type checking)
- **Monitoring**: Sentry, Prometheus metrics
- **Cloud Services**: Google Cloud Platform integration

**Frontend (Pro)**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Redux Toolkit
- **UI Components**: Custom design system
- **Forms**: React Hook Form with Yup validation
- **Testing**: Vitest, Cypress E2E, Storybook
- **Code Quality**: ESLint, Prettier, Stylelint

## API Structure Analysis

### 1. API Organization

The API follows a well-structured modular architecture located in `api/src/pcapi/`:

#### Core Application Structure
```
pcapi/
├── routes/               # API endpoints organized by domain
├── core/                # Business logic (domain-driven design)
├── models/              # Database models and mixins
├── infrastructure/      # External service integrations
├── tasks/               # Background task implementations
├── workers/             # Celery worker configurations
├── utils/               # Shared utilities
├── validation/          # Input validation logic
└── serialization/       # API response serialization
```

### 2. Flask API Integration with Spectree

The API uses **Spectree** as a sophisticated API documentation and validation framework, providing automatic OpenAPI/Swagger generation and type-safe request/response handling.

#### **Spectree Architecture**

**Extended Spectree Implementation:**
```python
# Custom ExtendedSpecTree class in api/src/pcapi/serialization/spec_tree.py
class ExtendedSpecTree(SpecTree):
    - Feature flag integration (routes hidden based on toggles)
    - Security scheme management
    - Humanized operation IDs
    - Custom response models
```

**API Schema Configuration:**
- **Multiple Schemas**: Separate schemas for public, deprecated, and collective APIs
- **Environment-Aware**: Different servers for integration/production
- **Security Schemes**: Bearer token and cookie-based authentication
- **Versioning Support**: URL-based API versioning strategy

#### **Route Decoration Pattern**

Routes use the `@spectree_serialize` decorator which provides:

```python
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.VENUES],
    response_model=venues_serialization.VenueResponse,
    resp=SpectreeResponse(HTTP_200=..., HTTP_404=...)
)
def get_venue_by_siret(siret: str) -> venues_serialization.VenueResponse:
    # Route implementation
```

**Key Features:**
- **Automatic Validation**: Request/response validation using Pydantic models
- **Documentation Generation**: Auto-generated OpenAPI specs with examples
- **Type Safety**: Full type checking for query params, body, and responses
- **Error Handling**: Standardized error response formatting
- **Security Integration**: Automatic security requirement documentation

#### **Blueprint Registration System**

Routes are installed from [app.py](api/src/pcapi/app.py)
[Source: api/src/pcapi/routes/public/__init__.py](api/src/pcapi/routes/public/__init__.py)
```python

# Routes organized by domain with separate Spectree schemas
public_api = Blueprint("public_api", __name__)
spectree_schemas.public_api_schema.register(public_api)

# Multiple API versions maintained simultaneously
deprecated_v2_prefixed_public_api = Blueprint(...)
deprecated_collective_public_api = Blueprint(...)
```

#### **Request/Response Flow**

1. **Incoming Request** → Flask route handler
2. **Spectree Validation** → Validates against Pydantic models
3. **Authentication Check** → API key or session validation
4. **Business Logic** → Core domain logic execution
5. **Response Serialization** → Pydantic model serialization
6. **Documentation Update** → Automatic OpenAPI spec generation

#### **API Documentation Strategy**

- **Live Documentation**: Generated OpenAPI specs served at runtime
- **Multiple Environments**: Environment-specific API documentation
- **Tag Organization**: Logical grouping of endpoints (VENUES, OFFERS, etc.)
- **Response Examples**: Comprehensive examples for all status codes
- **Security Documentation**: Automatic auth requirement documentation

#### Route Organization
The API endpoints are organized into logical groups:

- **`native/`** - Mobile application API (v1, v2)
- **`pro/`** - Professional/business interface API
- **`adage/`** - Educational marketplace integration
- **`public/`** - Public-facing API endpoints
- **`auth/`** - Authentication and authorization
- **`backoffice/`** - Administrative interface
- **`internal/`** - Internal system endpoints
- **`external/`** - Third-party integrations
- **`saml/`** - SAML authentication

### 3. Domain-Driven Design Implementation

The `core/` directory demonstrates strong domain-driven design principles:

#### Business Domains
- **`users/`** - User management and authentication
- **`offers/`** - Cultural offer management
- **`bookings/`** - Booking and reservation system
- **`finance/`** - Financial transactions and reimbursements
- **`offerers/`** - Cultural venue and provider management
- **`educational/`** - Educational program management
- **`fraud/`** - Fraud detection and prevention
- **`search/`** - Search functionality
- **`mails/`** - Email notification system
- **`geography/`** - Location-based services

Each domain typically contains:
- `models.py` - Domain entities and data models
- `api.py` - Business logic and service layer
- `repository.py` - Data access layer
- `factories.py` - Test data factories
- `exceptions.py` - Domain-specific exceptions
- `constants.py` - Domain constants

### 4. API Versioning Strategy

The API implements versioning through URL prefixes:
- Native API: `/native/v1/`, `/native/v2/`
- Adage API: `/adage/v1/`
- Public API: Multiple deprecated versions being maintained

### 5. Database Architecture

#### Model Organization
- **Base Classes**: `pc_object.py` provides common functionality
- **Mixins**: Reusable model behaviors (soft deletion, validation status, etc.)
- **Domain Models**: Organized by business domain
- **Migration System**: Alembic for database schema management

#### Key Model Patterns
- Soft deletion capabilities
- Validation status tracking
- Address standardization
- Thumbnail management for media

### 6. Background Processing

#### Task Organization
- **`celery_tasks/`** - Celery task definitions
- **`scheduled_tasks/`** - Periodic/cron-like tasks
- **`workers/`** - Worker process configurations

#### Queue Strategy
- Separate queues for different priorities and external calls
- Email tasks segregated by priority levels

### 7. External Integrations

#### Infrastructure Integrations
- **Google Cloud Services**: BigQuery, Cloud Storage, Cloud Tasks
- **Email Services**: Brevo (formerly Sendinblue)
- **Search**: Algolia integration
- **Monitoring**: Sentry error tracking
- **Authentication**: Google OAuth, SAML providers

#### Content Providers
- Multiple cultural content provider integrations
- Standardized provider interface patterns

## Frontend API Integration

### API Client Structure
The Pro frontend maintains a well-organized API client in `pro/src/apiClient/`:
- **Versioned Endpoints**: `v1/`, `v2/` following backend versioning
- **Domain-Specific Clients**: Separate modules for different API domains
- **Type Safety**: TypeScript integration with OpenAPI code generation

### Code Generation
- Automated API client generation from OpenAPI specifications
- Script-based workflow: `generate:api:client:local`

## Security Architecture

### Authentication & Authorization
- **Multi-layered Auth**: JWT tokens, session management, SAML integration
- **Role-based Access**: Different authentication flows for different user types
- **Security Headers**: Comprehensive security header implementation

### API Security Features
- CORS configuration
- Rate limiting capabilities
- Request/response logging with correlation IDs
- SQL injection prevention through ORM usage

## Testing Strategy

### Backend Testing
- **Unit Tests**: Comprehensive pytest suite
- **Integration Tests**: Database and external service testing
- **Test Organization**: Mirrors source code structure
- **Test Data**: Factory-based test data generation
- **Coverage**: High test coverage requirements

### Frontend Testing
- **Unit Tests**: Vitest for component testing
- **E2E Tests**: Cypress for end-to-end scenarios
- **Visual Testing**: Storybook for component documentation
- **Accessibility Testing**: Built-in a11y testing

## Application Component Management

### Component Instantiation Strategy

The Pass Culture codebase **does not use traditional dependency injection frameworks**. Instead, it employs a **factory pattern with settings-based backend selection** for managing stateful components and external service connections.

#### **Key Patterns Identified:**

**1. Backend Factory Pattern**
Components are instantiated ad-hoc during request lifecycle using factory functions:

[api/src/pcapi/connectors/big_query/backend.py](api/src/pcapi/connectors/big_query/backend.py)
```python
def get_backend() -> "BaseBackend":
    backend_class = import_string(settings.GOOGLE_BIG_QUERY_BACKEND)
    return backend_class()

# Usage in business logic
backend = big_query_connector.get_backend()
backend.run_query(query, page_size, **parameters)
```

**2. Settings-Driven Component Selection**

[api/src/pcapi/core/object_storage/__init__.py](api/src/pcapi/core/object_storage/__init__.py)
```python
BACKENDS_MAPPING = {
    GCP: "pcapi.core.object_storage.backends.gcp.GCPBackend",
    LOCAL_FILE_STORAGE: "pcapi.core.object_storage.backends.local.LocalBackend",
}

def _get_backends() -> set:
    providers = (settings.OBJECT_STORAGE_PROVIDER or "").split(",")
    return {BACKENDS_MAPPING[p] for p in providers}
```

**3. Component Instantiation Per Operation**
Each operation creates fresh instances:

[api/src/pcapi/core/object_storage/backends/gcp.py](api/src/pcapi/core/object_storage/backends/gcp.py)
```python
class GCPBackend(BaseBackend):
    def get_gcp_storage_client(self) -> Client:
        credentials = Credentials.from_service_account_info(self.bucket_credentials)
        return Client(credentials=credentials, project=self.project_id)  # New instance per call

    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        bucket = self.get_gcp_storage_client_bucket()  # Fresh connection
        gcp_cloud_blob = bucket.blob(storage_path)
        gcp_cloud_blob.upload_from_string(blob, content_type=content_type)
```

#### **Component Management Examples:**

**Google Cloud Services ([`api/src/pcapi/core/object_storage/backends/gcp.py`](api/src/pcapi/core/object_storage/backends/gcp.py))**
- **Pattern**: Fresh Google Cloud Storage clients created per operation
- **No Connection Pooling**: Each file operation instantiates new client
- **Authentication**: Service account credentials loaded from settings

**Search Backend ([`api/src/pcapi/core/search/__init__.py`](api/src/pcapi/core/search/__init__.py))**
- **Pattern**: `_get_backend()` called for every search operation
- **No Singleton**: New Algolia client instances created repeatedly
- **Configuration**: Backend class imported via settings string

**BigQuery Connector ([`api/src/pcapi/connectors/big_query/backend.py`](api/src/pcapi/connectors/big_query/backend.py))**
- **Pattern**: Lazy client instantiation with property caching
- **Partial Optimization**: Client cached within single backend instance
- **Lifecycle**: Backend instances still created per operation

**Google Drive Integration ([`api/src/pcapi/connectors/googledrive.py`](api/src/pcapi/connectors/googledrive.py))**
- **Pattern**: Service discovery API client built per operation
- **Authentication**: Kubernetes workload identity (no explicit credentials)
- **Testing**: Separate TestingBackend for development

#### **Implications of This Architecture:**

**Advantages:**
- **Environment Flexibility**: Easy switching between testing/production backends
- **Configuration Simplicity**: Settings-driven backend selection
- **Testing Support**: Mock backends for different environments
- **No Global State**: Avoid singleton-related issues

**Performance Considerations:**
- **Connection Overhead**: Fresh connections created for each operation
- **No Connection Pooling**: GCP/external service connections not reused
- **Memory Usage**: Multiple client instances in memory simultaneously
- **Authentication Cost**: Repeated credential loading and validation

#### **Multi-Backend Support**
Some services support multiple backends simultaneously:

[api/src/pcapi/core/object_storage/__init__.py](api/src/pcapi/core/object_storage/__init__.py)
```python
def store_public_object(folder: str, object_id: str, blob: bytes, content_type: str) -> None:
    for backend_path in _get_backends():  # Iterate over multiple backends
        backend = import_string(backend_path)
        backend(bucket_name=bucket).store_public_object(folder, object_id, blob, content_type)
```

This allows operations to write to multiple storage providers simultaneously (e.g., during migrations).

#### **Component Lifecycle Management**

**Database Connections:** Managed by SQLAlchemy through Flask app context
**External APIs:** Fresh instances per request/operation
**Background Tasks:** Celery workers with independent component instances
**Static Resources:** Settings-based configuration with environment switching

The architecture prioritizes **configuration flexibility** and **testing ease** over performance optimization through connection pooling or dependency injection frameworks.

## Development Operations

### Container Strategy
- **Docker Composition**: Separate containers for different services
- **Environment Management**: Multiple environment configurations
- **Development Tools**: Integrated debugging and profiling

### Deployment Pipeline
- **Environment Progression**: Testing → Staging → Production
- **Automated Deployment**: GitHub Actions-based CI/CD
- **Preview Environments**: Branch-based preview deployments

### Code Quality
- **Linting**: Comprehensive linting setup (Ruff, ESLint)
- **Type Checking**: MyPy for Python, TypeScript for frontend
- **Pre-commit Hooks**: Automated code quality checks
- **Dependency Management**: Poetry for Python, Yarn for Node.js

## Infrastructure

### Cloud Platform
- **Primary Platform**: Google Cloud Platform
- **Container Orchestration**: Google App Engine
- **Database**: Cloud SQL (PostgreSQL)
- **Object Storage**: Google Cloud Storage
- **Task Processing**: Google Cloud Tasks

### Monitoring & Observability
- **Error Tracking**: Sentry integration
- **Metrics**: Prometheus-based monitoring
- **Logging**: Structured logging with correlation tracking
- **Performance**: Request timing and profiling capabilities

## Key Strengths

1. **Clear Separation of Concerns**: Well-organized domain-driven architecture
2. **Comprehensive Testing**: High test coverage across all layers
3. **Type Safety**: Strong typing in both Python and TypeScript
4. **Security Focus**: Multiple layers of security implementation
5. **Scalable Architecture**: Microservice-ready structure with clear boundaries
6. **Development Experience**: Excellent tooling and automation
7. **Code Quality**: Strict linting and formatting standards
8. **Documentation**: Well-documented APIs and development processes

## Areas of Technical Complexity

1. **Legacy API Versions**: Multiple deprecated API versions requiring maintenance
2. **External Dependencies**: Numerous third-party integrations requiring management
3. **Multi-tenant Architecture**: Complex user role and permission management
4. **Financial Processing**: Sensitive financial transaction handling
5. **Compliance Requirements**: Educational and cultural sector regulations

## Conclusion

The Pass Culture codebase demonstrates enterprise-level software engineering practices with a clear, maintainable architecture. The API structure follows modern best practices with domain-driven design, comprehensive testing, and strong security measures. The separation between backend and frontend enables independent scaling and development while maintaining type safety and consistent interfaces.

The codebase is well-positioned for continued growth and feature development, with robust foundations for reliability, security, and maintainability.

---

*Audit conducted on: December 2024*
*Codebase version: Based on current main branch*