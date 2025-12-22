# AGENTS.md file

> **purpose** – This file is the onboarding manual for every AI assistant (Claude, Cursor, GPT, etc.) and every human who edits this repository.
> It encodes our coding standards, guard-rails, and workflow tricks so the *human 30 %* (architecture, tests, domain judgment) stays in human hands.[^1]
> Inspired by [julep AGENTS.md file](https://github.com/julep-ai/julep/blob/dev/AGENTS.md). See [diwank's article](https://diwank.space/field-notes-from-shipping-real-code-with-claude).

---

## 0. Project overview

pass Culture is a marketplace that connects cultural actors with teenagers living in France.
Credit is provided to teenagers to book cultural offers such as concerts, museum visits, books, and artistic equipment.

- **src/pcapi/core/**: Core modules
- **src/pcapi/routes/**: Routes exposed to front ends via OpenAPI and Swagger code generation
- **src/pcapi/routes/backoffice/**: Has its own Flask app and front end through Jinja templates

**Golden rule**: When unsure about implementation details or requirements, ALWAYS consult the developer rather than making assumptions.

---

## 1. Non-negotiable golden rules

| #: | AI *may* do                                                            | AI *must NOT* do                                                                    |
|---|------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| G-0 | Whenever unsure about something that's related to the project, ask the developer for clarification before making changes.    |  ❌ Write changes or use tools when you are not sure about something project specific, or if you don't have context for a particular feature/decision. |
| G-1 | Generate code **only inside** relevant source directories or explicitly pointed files.    | ❌ Touch `SPEC.md`, or any `*_spec.py` / `*.ward` files (humans own tests & specs). |
| G-2 | Add/update **`AIDEV-NOTE:` anchor comments** near non-trivial code edits. | ❌ Delete or mangle existing `AIDEV-` comments.                                     |
| G-3 | Follow lint/style configs (`pyproject.toml`, `.ruff.toml`, `.pre-commit-config.yaml`). Use the project's configured linter, if available, instead of manually re-formatting code. | ❌ Re-format code to any other style.                                               |
| G-4 | For changes >300 LOC or >3 files, **ask for confirmation**.            | ❌ Refactor large modules without human guidance.                                     |
| G-5 | Stay within the current task context. Inform the dev if it'd be better to start afresh.                                  | ❌ Continue work from a prior prompt after "new task" – start a fresh session.      |

---

## 2. Build, test & utility commands

If the commands are not available, first activate the virtual environment with `poetry shell`.

```bash
# Format, lint, type-check, test, codegen
ruff check --select I --config pyproject.toml --fix # sort imports
ruff format                                         # format
ruff check                                          # lint
flask shell                                         # spawn a python shell, useful to check that the Flask context loads
python src/pcapi/app.py                             # launch the backend in local dev environment
python src/pcapi/backoffice_app.py                  # launch the back office in local dev environment
pytest -m 'not backoffice'                          # launch the backend tests
pytest -m backoffice                                # launch the back office tests
```

For simple, quick Python script tests: `PYTHONPATH=$PWD python tests/test_file.py` (ensure correct CWD).

---

## 3. Coding standards

- **Python**: 3.11+, Flask, SQLAlchemy
- **Formatting**: `ruff` is configured in `pyproject.toml`
- **Typing**: `mypy` is configured in `pyproject.toml`
- **Naming**: `snake_case` (functions/variables), `PascalCase` (classes), `SCREAMING_SNAKE_CASE` (constants), and `camelCase` for SQLAlchemy model fields (for historic reasons).
- **Error Handling**: Typed exceptions; context managers for resources.
- **Documentation**: Google-style docstrings for public functions/classes.
- **Testing**: Separate test files matching source file patterns.

**Import style**

- The current standard is to import module files and rename them by prefixing with their module name.
- All module functions are called using the prefixed import.

Example:

```python

from pcapi.core.users import models as users_models

def update_user(user: users_models.User) -> None:
  pass

```

## 4. Project layout & Core Components

### Project Layout

| Directory                         | Description                                       |
| --------------------------------- | ------------------------------------------------- |
| `src/pcapi/core/`                   | Core business modules containing domain logic      |
| `src/pcapi/core/users/`             | User management (pro users, beneficiaries, backoffice users) |
| `src/pcapi/core/offers/`            | Cultural offers (products and events)             |
| `src/pcapi/core/offerers/`          | Cultural organizations that provide offers         |
| `src/pcapi/core/bookings/`          | Reservation system for offers                      |
| `src/pcapi/core/finance/`           | Credit management and invoicing system             |
| `src/pcapi/core/educational/`       | Educational offers for schools and institutions    |
| `src/pcapi/core/subscription/`      | Beneficiary registration and identity verification   |
| `src/pcapi/routes/`                 | API endpoints exposed to front-end applications    |
| `src/pcapi/routes/native/`          | Mobile app API endpoints                           |
| `src/pcapi/routes/pro/`             | Professional dashboard API endpoints               |
| `src/pcapi/routes/backoffice/`      | Internal administration interface                  |
| `src/pcapi/connectors/`             | External service integrations (APIs, file systems) |
| `tests/`                            | Test files mirroring source structure             |

### Module Structure

Each core module follows this file structure:

- **api.py**: Public functions for inter-module communication
- **schemas.py**: Pydantic models and dataclasses
- **models.py**: SQLAlchemy models
- **repository.py**: Database access layer using SQLAlchemy
- **factories.py**: FactoryBoy factories to use in tests and sandbox scripts

### Key Domain Models

- **Beneficiary**: Young person (15-18) who receives government cultural credit
- **Offerer**: Cultural organization that provides venues and offers
- **Venue**: Physical or digital location where cultural activities take place
- **Offer**: Cultural product or event available for booking
- **Booking**: Reservation made by a beneficiary for a specific offer
- **Deposit**: Government-allocated credit that beneficiaries can spend on culture
- **Fraud Check**: Identity verification process required for beneficiary activation
- **Subscription Flow**: Multi-step registration process for new beneficiaries

---

## 5. Anchor comments

Add specially formatted comments throughout the codebase, where appropriate, for yourself as inline knowledge that can be easily `grep`ped for.

### Guidelines

- Use `AIDEV-NOTE:`, `AIDEV-TODO:`, or `AIDEV-QUESTION:` (all-caps prefix) for comments aimed at AI and developers.
- Keep them concise (≤ 120 chars).
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.
- **Update relevant anchors** when modifying associated code.
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction.
- Make sure to add relevant anchor comments, whenever a file or piece of code is:
  - too long, or
  - complex, or
  - critical, or
  - confusing, or
  - could have a bug unrelated to the task you are currently working on.

Example:

```python
# AIDEV-NOTE: perf-hot-path; avoid extra allocations (see ADR-24)
def render_feed(...):
    ...
```

---

## 6. Commit discipline

- **Granular commits**: One logical change per commit.
- **Tag AI-generated commits**: e.g., `feat: optimise feed query [AI]`.
- **Clear commit messages**: Explain the *why*; link to issues/ADRs if architectural.
- **Use `git worktree`** for parallel/long-running AI branches (e.g., `git worktree add ../wip-foo -b wip-foo`).
- **Review AI-generated code**: Never merge code you don't understand.

---

## 7. API models & codegen

- To modify API models, **edit the Pydantic models** in `src/pcapi/routes/**/serializers.py`.
- **Regenerate code** after OpenAPI changes: `bash src/scripts/generate_openapi_code.sh` (from project root).
- **Do NOT manually edit** generated files as they will be overwritten.

**Spectree example**:

```python
from spectree import BaseModel, Tag, Response
from pcapi.routes.serialization import BaseModel as PCBaseModel

class MyRequestModel(PCBaseModel):
    field: str

class MyResponseModel(PCBaseModel):
    result: str

# Use in route with @blueprint.route decorator and spectree validation
```

---

### 8. Pytest testing framework

- Use descriptive test names: `def test_descriptive_scenario():`.
- Use the `db_session` fixture to isolate the tests database.
- Ensure correct working directory (e.g., `api/`) for tests.
- Activate virtual environment: `poetry shell`.
- Limit failures for faster feedback: `pytest --fail-limit 1 module_to_test.py`.

---

## 10. Directory-Specific AGENTS.md Files

- **Always check for `AGENTS.md` files in specific directories** before working on code within them. These files contain targeted context.
- If a directory's `AGENTS.md` is outdated or incorrect, **update it**.
- If you make significant changes to a directory's structure, patterns, or critical implementation details, **document these in its `AGENTS.md`**.
- If a directory lacks a `AGENTS.md` but contains complex logic or patterns worth documenting for AI/humans, **suggest creating one**.

---

## 11. Common pitfalls

- Wrong current working directory for commands/tests (e.g., ensure you are in `pass-culture-main/api/`, not in the `pass-culture-main/` root folder).
- Forgetting to `poetry shell`.
- Large AI refactors in a single commit (makes `git bisect` difficult).
- Delegating test/spec writing entirely to AI (can lead to false confidence).

---

## 13. Key File & Pattern References

This section provides pointers to important files and common patterns within the codebase.

**API Route Definitions**:

- Location: `src/pcapi/routes/**/*.py` (e.g., `src/pcapi/routes/native/v1/subscription.py`)
- Pattern: Flask blueprints with spectree decorators for OpenAPI generation
- Request/Response models: Pydantic BaseModel classes in `serialization.py` files
- Example: `src/pcapi/routes/native/v1/serialization/subscription.py`

**Serialization Models** (Pydantic):

- Location: `src/pcapi/routes/**/serialization.py` or `serializers.py`
- Pattern: Inherit from `pcapi.routes.serialization.BaseModel`
- Use `alias_generator = to_camel` for camelCase JSON fields
- Configuration: `orm_mode = True` for SQLAlchemy model conversion

**ORM Models** (SQLAlchemy):

- Location: `src/pcapi/core/**/models.py` (e.g., `src/pcapi/core/users/models.py`)
- Pattern: Inherit from `PcObject` or `Model` base classes
- Use `camelCase` for field names (historic reasons)
- Include type hints and relationships

**API Endpoints for Inter-Module Communication**:

- Location: `src/pcapi/core/**/api.py` files
- Pattern: Public functions that other modules can import and use
- Example: `src/pcapi/core/subscription/api.py`

**Database Repositories**:

- Location: `src/pcapi/core/**/repository.py`
- Pattern: Database access layer using SQLAlchemy queries
- Encapsulate complex database operations

**Factory Classes** (For Testing):

- Location: `src/pcapi/core/**/factories.py`
- Pattern: FactoryBoy factories for creating test data
- Used in tests and sandbox scripts

**Schema Definitions** (Data Classes):

- Location: `src/pcapi/core/**/schemas.py`
- Pattern: Pydantic models and dataclasses for business logic
- Example: `src/pcapi/core/subscription/schemas.py`

**External Connectors**:

- Location: `src/pcapi/connectors/**/`
- Pattern: Adapters for external services (APIs, file systems)
- Include serialization models for external API responses

**Test Files**:

- Location: `tests/**/*_test.py`
- Pattern: Mirror source file structure, use descriptive test names
- Use `db_session` fixture for database isolation

---

## 14. Domain-Specific Terminology

**Core Business Entities**:

- **Beneficiary**: Young person (15-18) who receives cultural credit from the French government
- **Offerer**: Cultural actor/organization that provides offers (venues, events, products)
- **Venue**: Physical or digital location where cultural offers are available
- **Offer**: Cultural product or event (concert, book, museum visit, etc.)
- **Booking**: Reservation of an offer by a beneficiary
- **Credit/Deposit**: Government-provided funds for beneficiaries to spend on cultural offers

**User Types**:

- **Pro User**: Professional user representing an offerer/venue
- **Backoffice User**: Internal staff with administrative privileges
- **Underage Beneficiary**: 15-17 year old with limited credit
- **18+ Beneficiary**: 18 year old with full credit access
- **Free Beneficiary**: User with free access to certain offers

**Subscription & Identity Verification**:

- **DMS**: French government document management system for identity verification
- **Ubble**: Third-party identity verification service
- **Educonnect**: French education system identity provider
- **Jouve**: Legacy identity verification provider
- **Fraud Check**: Identity/eligibility verification process
- **Subscription Flow**: Multi-step process for beneficiaries to activate their credit

**Financial Terms**:

- **Deposit**: Financial credit allocated to beneficiaries
- **Reimbursement**: Payment from pass Culture to offerers for bookings
- **Pricing**: Offer cost structure and beneficiary payment rules
- **Finance API**: System for managing payments and reimbursements

**Geographical Terms**:

- **IRIS**: French statistical geographical unit
- **Department**: French administrative division
- **Region**: French administrative region

**Technical Terms**:

- **Feature Toggle**: Runtime configuration flags for enabling/disabling features
- **Spectree**: OpenAPI documentation generation library
- **PCObject**: Base SQLAlchemy model class with common fields
- **Serialization**: Data transformation between API and database models

**Educational Context**:

- **Collective Offer**: Group bookings for schools and educational institutions
- **Educational Institution**: Schools and educational organizations
- **Institutional**: Relating to educational/collective bookings vs individual bookings

**External Integrations**:

- **Provider**: External service that supplies offer data
- **Allocine**: Movie database integration
- **Titelive**: Book database integration
- **CGR**: Cinema chain integration

---

## 15. Meta: Guidelines for updating AGENTS.md files

### Elements that would be helpful to add

1. **Decision flowchart**: A simple decision tree for "when to use X vs Y" for key architectural choices would guide my recommendations.
2. **Reference links**: Links to key files or implementation examples that demonstrate best practices.
3. **Domain-specific terminology**: A small glossary of project-specific terms would help me understand domain language correctly.
4. **Versioning conventions**: How the project handles versioning, both for APIs and internal components.

### Format preferences

1. **Consistent syntax highlighting**: Ensure all code blocks have proper language tags (`python`, `bash`, etc.).
2. **Hierarchical organization**: Consider using hierarchical numbering for subsections to make referencing easier.
3. **Tabular format for key facts**: The tables are very helpful - more structured data in tabular format would be valuable.
4. **Keywords or tags**: Adding semantic markers (like `#performance` or `#security`) to certain sections would help me quickly locate relevant guidance.

[^1]: This principle emphasizes human oversight for critical aspects like architecture, testing, and domain-specific decisions, ensuring AI assists rather than fully dictates development.

---

# AI Assistant Workflow: Step-by-Step Methodology

When responding to user instructions, the AI assistant (Claude, Cursor, GPT, etc.) should follow this process to ensure clarity, correctness, and maintainability:

1. **Consult Relevant Guidance**: When the user gives an instruction, consult the relevant instructions from `AGENTS.md` files (both root and directory-specific) for the request.
2. **Clarify Ambiguities**: Based on what you could gather, see if there's any need for clarifications. If so, ask the user targeted questions before proceeding.
3. **Break Down & Plan**: Break down the task at hand and chalk out a rough plan for carrying it out, referencing project conventions and best practices.
4. **Trivial Tasks**: If the plan/request is trivial, go ahead and get started immediately.
5. **Non-Trivial Tasks**: Otherwise, present the plan to the user for review and iterate based on their feedback.
6. **Track Progress**: Use a to-do list (internally, or optionally in a `TODOS.md` file) to keep track of your progress on multi-step or complex tasks.
7. **If Stuck, Re-plan**: If you get stuck or blocked, return to step 3 to re-evaluate and adjust your plan.
8. **Update Documentation**: Once the user's request is fulfilled, update relevant anchor comments (`AIDEV-NOTE`, etc.) and `AGENTS.md` files in the files and directories you touched.
9. **User Review**: After completing the task, ask the user to review what you've done, and repeat the process as needed.
10. **Session Boundaries**: If the user's request isn't directly related to the current context and can be safely started in a fresh session, suggest starting from scratch to avoid context confusion.
