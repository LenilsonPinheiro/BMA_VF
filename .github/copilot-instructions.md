# AI Coding Agent Instructions for BMA_VF

## Project Overview

**Belarmino Monteiro Advogado** is a Flask-based law firm website with a CMS admin panel for managing dynamic content. The application uses SQLAlchemy (ORM), Flask-WTF (forms), Flask-Login (authentication), and Flask-Migrate (database versioning). It's designed for Google App Engine deployment but runs on SQLite locally.

**Key Architecture**: Multi-blueprint route structure (`main_routes`, `auth_routes`, `admin_routes`) feeding Jinja2 templates with content from a database-backed content management system.

---

## 🌳 Branching & Contribution Workflow (MANDATORY)

**Golden Rule**: Never commit directly to `main`. All changes must go through a Pull Request.

1.  **Create a Branch**: Create a new branch from `main` named `feature/<description>` or `fix/<description>`.
2.  **Develop**: Make your code changes on this new branch.
3.  **Local Checks**: Before pushing, run `python verify_ecosystem.py` and `python run_all_tests.py` locally. Fix any issues.
4.  **Pull Request**: Push your branch and open a PR against `main`.
5.  **Automated Review**: A GitHub Action will run all checks (`detect-secrets`, `black --check`, tests, ecosystem sync). The PR merge will be **blocked** if any check fails.
6.  **Manual Review**: Await human review and approval.
7.  **Merge**: Once approved, the PR can be merged.

---

## Critical Developer Workflows

### Local Development Setup
```powershell
# All local development starts here
.\run.ps1
```
This PowerShell script orchestrates: venv activation → pip install → database initialization → Flask dev server startup on `http://127.0.0.1:5000`. The script calls `auto_fix.py` for database consistency checks.

**Clean database reset:**
```powershell
.\run.ps1 clean
```
Removes `site.db` and `migrations/` folder before rebuilding—use when schema corruption occurs.

### Database Migrations
- **Location**: `migrations/` (managed by Alembic via Flask-Migrate)
- **Key file**: `migrations/env.py` configures migration behavior
- Use `flask db migrate -m "description"` → `flask db upgrade` workflow
- **Important**: The `ensure_essential_data()` function in `BelarminoMonteiroAdvogado/__init__.py` runs on app startup to guarantee core pages/content exist

### Testing
- Test fixtures in `test_app.py` use in-memory SQLite (`sqlite:///:memory:`) with CSRF disabled
- The master runner `run_all_tests.py` automatically discovers and executes all `test_*.py` files in the root directory.
- **To add a new test suite**: Create a file named `test_your_feature.py`. It will be picked up automatically.
- **To make a test critical for deployment**: Add the filename to the `CRITICAL_TESTS` list inside `run_all_tests.py`.
- **To run a specific test for faster debugging**: Follow the `PYTEST_USAGE_GUIDE.md`.

---

## Architecture Patterns

### 1. Content Model: Database-Driven Pages
The system separates **structure** (what pages exist) from **content** (what they display):

- **`Pagina` model** (`models.py`): Defines pages with slugs, templates, hierarchy, ordering. Example: `slug='home'` → `template_path='home/index.html'`
- **`ConteudoGeral` model**: Stores all editable content as `(pagina, secao, conteudo)` tuples. Example: `pagina='home', secao='titulo'` stores the hero title
- **Rendering function**: `render_page(template_name, page_identifier)` in `__init__.py` fetches both structure and content from DB, passes context to Jinja2

**Pattern**: To add a new page element, create a `ConteudoGeral` entry with matching `secao` name, then reference it in the template as `{{ secao_name }}`.

### 2. Blueprint Organization
Three blueprints handle routing:
- **`main_bp`** (`main_routes.py`): Public routes (home `/`, services `/areas-de-atuacao`, contact `/contato`, dynamic slugs `/<path:slug>`)
- **`auth_bp`** (`auth_routes.py`): Login/logout/password management
- **`admin_bp`** (`admin_routes.py`): Admin dashboard, content CRUD operations

**Blueprint registration** happens in `routes/__init__.py` → imported and registered in `create_app()` in `BelarminoMonteiroAdvogado/__init__.py`

### 3. Theme Configuration
- **`ThemeSettings` model**: Stores active theme (option1–option4)
- **`home()` route** dynamically selects template based on `ThemeSettings.theme` (e.g., theme='option4' → `home/home_option4.html`)
- Each theme variant lives in `templates/home/home_option[1-4].html`

### 4. Image Processing
- **Location**: `image_processor.py`
- **Pattern**: On upload, `process_and_save_image()` auto-converts to WebP at 95% quality, redimensions, creates backups
- Uploaded files stored in `static/images/uploads/` with secure filenames using `secrets.token_hex()`

---

## Project-Specific Conventions

### Form Handling
- All forms extend `FlaskForm` from `forms.py`
- **Important**: Admin forms include CSRF token via `EmptyForm` in `admin_routes.py` to maintain session security
- File uploads validated via `allowed_file()` helper checking against `ALLOWED_EXTENSIONS` config
- **Critical Method Name**: Use `user.check_password(password)` not `verify_password()` - this is the actual method in the User model

### Config & Secrets
- Database path: `instance/site.db` (SQLite, created automatically)
- Environment variables loaded via `.env` (via `python-dotenv`)
- **GAE deployment**: Uses `app.yaml` with Gunicorn; `DATABASE_URL` env var can override local SQLite

### Database Event Listeners
- SQLAlchemy `@event.listens_for(Model, 'before_update')` decorators auto-update `Pagina.data_modificacao` when related content changes
- **Example**: Editing `ConteudoGeral` for page 'home' auto-updates the home page's modification timestamp

### Jinja2 Filters & Context
- **Custom filters**: `from_json_filter` for parsing JSON strings in templates
- **Global context functions**: `get_nav_pages()` and `get_page_content()` run on every render to populate navigation and page content

---

## Admin Routes Deep Dive

### Dashboard Architecture
The admin dashboard (`/admin/dashboard`) is a unified single-page app approach:
- **Query parameter navigation**: `?page=Services` or `?page=Team` selects which content section to display
- **Context passed to template**: `selected_page`, `content_for_page`, `all_content_pages`, `nav_pages_admin`
- **Multiple forms in one template**: `password_form`, `theme_form`, `form` (EmptyForm for CSRF) all passed to `admin/dashboard.html`

### Key Admin Routes Pattern
```python
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    selected_page = request.args.get('page', 'configuracoes_gerais')
    content_for_page = ConteudoGeral.query.filter_by(pagina=selected_page).all()
    # Passes all data needed by tabs/sections in the dashboard template
    return render_template('admin/dashboard.html', selected_page=selected_page, 
                          content_for_page=content_for_page, ...)
```

### Content Update Route
```python
@admin_bp.route('/update-content', methods=['POST'])
@login_required
def update_content():
    # Handles both text fields (ConteudoGeral) and file uploads
    # Text: keys like 'content-123' where 123 is ConteudoGeral.id
    # Files: processed through process_and_save_image() or save_logo()
```
- Always wrap in try/except per field to avoid one bad upload breaking all updates
- File handling: Use `process_and_save_image()` from `image_processor.py`, never raw Werkzeug saves

### Compatibility Redirect Routes
These routes exist for backward compatibility—they redirect to the unified dashboard:
```python
@admin_bp.route('/manage-areas') → redirects to dashboard?page=Services
@admin_bp.route('/manage-team') → redirects to dashboard?page=Team
@admin_bp.route('/manage-clients') → redirects to dashboard?page=Clients
```

---

## Authentication Routes Deep Dive

### Login Flow (`auth_routes.py`)
- **Blueprint prefix**: Uses `/auth` url_prefix to separate auth routes from public routes
- **Open Redirect Protection**: `is_safe_url()` validates next page parameter to prevent redirect attacks
- **Password Check**: Must use `user.check_password(password)` from User model, not a non-existent `verify_password()` method
- **Session Management**: Uses Flask-Login's `login_user()` / `logout_user()` decorators

### Example Login Route
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))  # Already logged in
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):  # ← Correct method
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(request.args.get('next', url_for('admin.dashboard')))
    
    return render_template('auth/login.html', form=form)
```

---

## Template Structure & Inheritance

### Base Templates Hierarchy
- **`base.html`**: Main base with HTML5 boilerplate, navigation, footer, flash messages
- **`base_option[1-8].html`**: Theme-specific base templates (extends `base.html`)
- **Admin templates**: All under `templates/admin/` (e.g., `dashboard.html`, `login.html`)
- **Public templates**: Organized by feature (e.g., `home/`, `contato/`, `areas_atuacao/`)

### Dynamic Content in Templates
```html
<!-- Reference ConteudoGeral content by secao name -->
<h1>{{ titulo }}</h1>
<p>{{ paragrafo }}</p>

<!-- For JSON content use custom filter -->
{% set config = google_analytics_config|from_json_filter %}
<script>ga({{ config.tracking_id }})</script>
```

### Key Template Variables Automatically Provided
These are injected by `render_page()` and app context processors:
- `nav_pages`: List of Pagina objects for main navigation
- All ConteudoGeral entries for current page as template variables (by `secao` name)
- `current_user`: Flask-Login user object (for `@login_required` pages)

---

## App Initialization & Blueprint Registration

### Application Factory Flow (`create_app()` in `__init__.py`)

```python
def create_app():
    """Cria e configura a instância da aplicação Flask."""
    app = Flask(__name__, instance_relative_config=True)
    
    # 1. Config: Database, uploads, allowed extensions
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'mp4', 'webm'}
    
    # 2. Initialize extensions (db, migrate, login_manager, csrf, etc.)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CSRFProtect(app)
    
    # 3. Register Jinja2 filters (from_json_filter, get_file_mtime)
    app.jinja_env.filters['from_json_filter'] = from_json_filter
    app.jinja_env.filters['get_file_mtime'] = get_file_mtime
    
    # 4. Register app context processors (nav_pages, page_content in every render)
    app.context_processor(get_nav_pages)
    app.context_processor(get_page_content_processor)
    
    # 5. Register blueprints with appropriate prefixes
    app.register_blueprint(main_bp)                              # No prefix: routes at /
    app.register_blueprint(admin_bp, url_prefix='/admin')        # Routes at /admin/...
    app.register_blueprint(auth_bp, url_prefix='/auth')          # Routes at /auth/...
    
    # 6. Register CLI commands (flask init-db)
    @app.cli.command('init-db')
    def init_db():
        ensure_essential_data()
        db.session.commit()
    
    return app
```

### Blueprint Prefixes Summary
| Blueprint | Prefix | Example Routes |
|-----------|--------|-----------------|
| `main_bp` | None | `/`, `/areas-de-atuacao`, `/<path:slug>` |
| `admin_bp` | `/admin` | `/admin/dashboard`, `/admin/update-content` |
| `auth_bp` | `/auth` | `/auth/login`, `/auth/logout` |

---

## Common Debugging Scenarios

### Database Inconsistency (Migration Conflicts)
**Symptom**: "Table already exists" or migration version mismatch
**Solution**:
```powershell
.\run.ps1 clean
# This removes site.db and migrations/, then rebuilds from scratch
# The ensure_essential_data() function repopulates core content
```

### Admin Dashboard Not Showing Content
**Symptom**: Selected page tab has no content_for_page items
**Debug**:
```python
# From flask shell
>>> from BelarminoMonteiroAdvogado.models import ConteudoGeral
>>> ConteudoGeral.query.filter_by(pagina='your_page_slug').all()
# If empty, the ensure_essential_data() didn't create it or was removed
# Add missing content via admin or manually in shell
```

### Images Not Converting to WebP
**Symptom**: Uploaded images stay in original format (jpg/png)
**Debug**: Check `image_processor.py` execution—look for PIL errors:
```python
>>> from BelarminoMonteiroAdvogado.image_processor import process_and_save_image
>>> process_and_save_image('/path/to/image.jpg', '/path/to/output.webp')
# Returns (success_bool, original_size, optimized_size, output_path)
```

### Login Always Fails (401 Unauthorized)
**Symptom**: Correct credentials rejected
**Common Causes**:
1. **Wrong password method**: Using `verify_password()` instead of `check_password()`
2. **User not in DB**: Admin user created during `flask init-db` but missing if DB was reset
3. **CSRF token issues**: Ensure `LoginForm` includes `{{ form.hidden_tag() }}`

**Fix**:
```python
# Verify admin exists in shell
>>> from BelarminoMonteiroAdvogado.models import User
>>> User.query.all()
# If empty, recreate via:
>>> flask init-db  # or manually add user in shell
```

### Migrations Won't Upgrade ("Can't locate revision identified by...")
**Symptom**: `flask db upgrade` fails with revision error
**Solution**:
```bash
flask db stamp head  # Reset migration head pointer
flask db migrate -m "description"  # Create new migration
flask db upgrade  # Apply it
```

---

## Data Models Deep Dive

### Core Models and Their Relationships

**`Pagina` (Pages)** - Hierarchical page structure
- `slug`: Unique identifier (e.g., 'home', 'sobre-nos', 'areas-de-atuacao')
- `template_path`: Which Jinja2 template to render (e.g., 'home/index.html', 'areas_atuacao/servico_base.html')
- `tipo`: Page type ('pagina_geral', 'servico', 'area_atuacao') - determines behavior and rendering
- `parent_id`: Enables hierarchical menus (e.g., parent=áreas-de-atuacao, children=[direito-civil, direito-do-consumidor])
- `show_in_menu` / `ativo`: Control visibility and publication
- `data_modificacao`: Auto-updated by event listeners when related content changes

**`ConteudoGeral` (Content Storage)** - Database-backed content for any page
- Composite key pattern: `(pagina, secao)` uniquely identifies a content piece
- `secao`: Section identifier (e.g., 'titulo', 'paragrafo', 'hero_show_button', 'google_analytics_config')
- `field_type`: Data type ('text', 'textarea', 'boolean', 'image', 'video', 'json')
- **Query Pattern**: Always filter by BOTH `pagina` and `secao` to get specific content
  ```python
  ConteudoGeral.query.filter_by(pagina='home', secao='titulo').first()
  ```

**`AreaAtuacao` (Services/Practice Areas)** - Law practice areas
- Creates auto-linked `Pagina` record with `slug=area_slug` and `tipo='servico'`
- `icone`: Bootstrap Icons class (e.g., 'bi bi-bank', 'bi bi-shield-check')
- Event listener auto-updates parent page's `data_modificacao` when modified

**`MembroEquipe` (Team Members)** - Law firm attorneys and staff
- `foto`: Path to WebP image (processed through `image_processor.py`)
- `biografia`: Rich text biography
- Displayed on home page via `HomePageSection` with `section_type='show_team_on_home'`

**`Depoimento` (Client Testimonials)** - Public testimonials
- `token_submissao`: Unique token for form submission links
- `aprovado`: Boolean flag - only approved testimonials display
- Displayed via `HomePageSection` with `section_type='show_testimonials'`

**`ThemeSettings` (Global Theme Config)** - Single record manages entire site theme
- `theme`: Active theme variant ('option1', 'option2', etc.)
- Color fields: `cor_primaria_tema1` through `cor_primaria_tema4` + dark mode variants
- Controls which `templates/home/home_option[N].html` template renders on home page

**`HomePageSection` (Home Page Block Manager)** - Controls what displays on home page
- `section_type`: Type of section ('hero', 'show_services', 'show_team_on_home', 'show_testimonials', 'show_clients')
- `order`: Display sequence
- `is_active`: Enable/disable sections without deleting
- Admin dashboard reorders these via AJAX to `@admin_bp.route('/reorder-home-sections')`

---

## Key Files & Their Responsibilities

| File | Purpose |
|------|---------|
| `BelarminoMonteiroAdvogado/__init__.py` | App factory, blueprint registration, core content loading, CLI commands |
| `BelarminoMonteiroAdvogado/models.py` | SQLAlchemy model definitions (User, Pagina, ConteudoGeral, AreaAtuacao, etc.) |
| `BelarminoMonteiroAdvogado/forms.py` | WTForms definitions for login, contact, theme management |
| `routes/main_routes.py` | Public-facing routes (home, services, contact, dynamic pages) |
| `routes/admin_routes.py` | Admin panel CRUD operations (largest file: 457 lines) |
| `routes/auth_routes.py` | Authentication (login, logout, password reset) |
| `BelarminoMonteiroAdvogado/image_processor.py` | Automatic image optimization & WebP conversion |
| `migrations/` | Alembic database version control |
| `templates/` | Jinja2 templates organized by feature (home/, admin/, etc.) |

---

## Content Flow: From Database to Template

### Data Flow for a Single Page Render

1. **User requests** `/areas-de-atuacao` (service listing)
2. **Route handler** (`main_routes.py`) executes:
   ```python
   @main_bp.route('/areas-de-atuacao')
   def todas_areas_atuacao():
       areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
       return render_page('areas_atuacao/todas_areas.html', 'todas_areas', areas=areas)
   ```

3. **`render_page()` function** (in `__init__.py`):
   - Calls `get_page_content('todas_areas')` which queries `ConteudoGeral.query.filter_by(pagina='todas_areas')`
   - Returns dict with all content for that page keyed by `secao` name
   - Merges with extra context (in this case, `areas=areas`)

4. **Template renders** with combined context:
   ```html
   <h1>{{ titulo }}</h1>  <!-- From ConteudoGeral -->
   <p>{{ paragrafo }}</p>
   <div class="services">
       {% for area in areas %}  <!-- From route handler -->
           <div class="service-card">{{ area.titulo }}</div>
       {% endfor %}
   </div>
   ```

### Service/Area Detail Page Flow

1. **User requests** `/<path:slug>` (e.g., `/direito-civil`)
2. **Catch-all route handler**:
   ```python
   @main_bp.route('/<path:slug>')
   def dynamic_page(slug):
       pagina = Pagina.query.filter_by(slug=slug).first_or_404()
       return render_page(pagina.template_path, slug)
   ```

3. **For service areas** (`AreaAtuacao`), `template_path='areas_atuacao/servico_base.html'`
4. **Template searches** for content with `pagina=slug` (e.g., `pagina='direito-civil'`)
5. **Event listener** in models ensures `Pagina.data_modificacao` updates when related `ConteudoGeral` changes

---

## Common Modification Scenarios

### Add a New Admin Content Field
1. Create `ConteudoGeral` entry in `ensure_essential_data()` with new `secao` name
2. Add form field in `admin_routes.py` 's edit endpoint (look for `@admin_bp.route('/update-content')`)
3. Reference in admin template as `{{ secao_name }}` and in dashboard as part of `content_for_page` list
4. If field stores JSON, add form validation before calling `render_page()`

### Create a New Service/Area of Practice
This pattern is CRITICAL - it demonstrates how the system auto-links database records:

1. **Add `AreaAtuacao` record** (via admin dashboard form):
   ```python
   new_service = AreaAtuacao(
       slug='direito-tributario',           # URL slug
       titulo='Direito Tributário',          # Display name
       descricao='Assessoria em questões tributárias e fiscais',
       icone='bi bi-percent',               # Bootstrap icon
       ordem=5
   )
   db.session.add(new_service)
   ```

2. **`ensure_essential_data()` auto-creates linked `Pagina`** (on next app startup):
   ```python
   db.session.add(Pagina(
       slug=service_data['slug'],           # Matches AreaAtuacao.slug
       titulo_menu=service_data['titulo'],
       tipo='servico',                      # Special type
       template_path='areas_atuacao/servico_base.html',
       parent=parent_page,                  # Parent is /areas-de-atuacao
       ativo=True,
       show_in_menu=True,
       ordem=service_data['ordem']
   ))
   ```

3. **Template `areas_atuacao/servico_base.html`** automatically receives:
   - All `ConteudoGeral` entries where `pagina='direito-tributario'`
   - Referenced in template as `{{ titulo }}`, `{{ paragrafo }}`, etc.

4. **URL routing**: Catch-all route `/<path:slug>` matches `/direito-tributario` and renders the template

5. **Icon field**: Uses **Bootstrap Icons** classes—available icons at https://icons.getbootstrap.com/ (e.g., `bi bi-bank`, `bi bi-gavel`, `bi bi-shield-check`)

### Create a New Page
1. Add `Pagina` record with unique `slug`, `template_path`, set `show_in_menu=True` if needed
2. Create corresponding Jinja2 template at `template_path` location
3. Template automatically receives context from `get_page_content(slug)` via `render_page()`
4. Catch-all route `/<path:slug>` in `main_routes.py` handles dynamic page routing

### Change Theme
- Modify `ThemeSettings.theme` value via admin or database
- `home()` route in `main_routes.py` selects template based on this: `theme='option4'` → `home/home_option4.html`
- Add new template variant to `templates/home/home_option[N].html`
- Theme-specific CSS in `static/css/` (or inline in theme-specific template)

### Add New Team Member or Testimonial
1. Create `MembroEquipe` or `Depoimento` record via admin panel
2. For images: Use `process_and_save_image()` from `image_processor.py`, store path in `foto` or `logo_cliente` field
3. Home page automatically displays via `HomePageSection` with type 'show_team_on_home' or 'show_testimonials'

### Deploy Changes
- Local: `.\run.ps1` restarts server with database migrations applied
- GAE: `gcloud app deploy` reads `app.yaml`, uses Gunicorn, connects to production database via `DATABASE_URL`

## Testing Guidance

- **Test patterns**: Use in-memory SQLite, disable CSRF, create admin user in fixture
- **Admin routes**: Require login (enforce via `@login_required` decorator)
- **File upload tests**: Mock `werkzeug.FileStorage` or use `test_uploads/` temp folder
- **Gotcha**: Admin dashboard forms expect `EmptyForm` instance in context for CSRF token availability

### Test Fixture Pattern
```python
@pytest.fixture
def app():
    """Creates app instance for testing with in-memory database."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER": "./test_uploads"
    })
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create test admin
        admin = User(username='admin', password_hash=generate_password_hash('admin'))
        db.session.add(admin)
        db.session.commit()
            
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app): 
    return app.test_client()

# Test login flow
def test_login_success(client):
    response = client.post('/auth/login', 
        data={'username': 'admin', 'password': 'admin'}, 
        follow_redirects=True)
    assert response.status_code == 200
    assert b"dashboard" in response.data.lower()
```

---

## Email Configuration & Contact Form

### Email Settings Storage Pattern
Email configuration is stored in `ConteudoGeral` with `pagina='configuracoes_email'`:
- `smtp_server`: SMTP host (e.g., 'smtp.gmail.com')
- `smtp_port`: Port number (e.g., '587' for TLS)
- `smtp_user`: Sender email address
- `smtp_pass`: SMTP password or app-specific password
- `email_to`: Recipient email address

### Contact Form Flow
```python
@main_bp.route('/contato', methods=['GET', 'POST'])
def pagina_contato():
    form = ContactForm()
    if form.validate_on_submit():
        # Fetch email config from database
        email_settings_db = ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()
        email_config = {item.secao: item.conteudo for item in email_settings_db}
        
        # Send email using config values
        SMTP_SERVER = email_config.get('smtp_server')
        SMTP_PORT = int(email_config.get('smtp_port', 587))
        SMTP_USER = email_config.get('smtp_user')
        SMTP_PASS = email_config.get('smtp_pass')
        EMAIL_TO = email_config.get('email_to')
        
        # MIMEMultipart email construction...
```

### Gmail Configuration Example
1. Enable 2FA on Gmail account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Store in admin dashboard:
   - `smtp_server`: smtp.gmail.com
   - `smtp_port`: 587
   - `smtp_user`: your-email@gmail.com
   - `smtp_pass`: (app-specific password)
   - `email_to`: where-to-send@example.com

---

## Deployment Notes

### Google App Engine Configuration
- **Config file**: `app.yaml` (Gunicorn, worker count, environment)
- **Entry point**: `gunicorn -b :$PORT main:app` (serves `main.py` which imports from `BelarminoMonteiroAdvogado`)
- **Static files**: Served via handlers at `/static` with 1-day cache (`expiration: "1d"`)
- **Automatic scaling**: F1 instance class, min 0 / max 1, 65% CPU target
- **Environment**: `FLASK_ENV: production` and `SECRET_KEY` configured

### Database Deployment
- **Local development**: SQLite at `instance/site.db`
- **Production**: `DATABASE_URL` environment variable (expects PostgreSQL or compatible)
  - GAE Cloud SQL PostgreSQL is recommended
  - Set via GAE environment editor or `gcloud app deploy`

### Static Files & Uploads
- **CSS/JS**: `BelarminoMonteiroAdvogado/static/css/` and `js/`
- **User uploads**: `BelarminoMonteiroAdvogado/static/images/uploads/` (must be writable)
- **Cache busting**: Templates use `{{ 'css/style.css'|get_file_mtime }}` for versioning

### Pre-Deployment Checklist
```bash
# 1. Run tests
pytest test_app.py -v

# 2. Create migration if schema changed
flask db migrate -m "description"
flask db upgrade

# 3. Verify admin user exists
flask shell
>>> from BelarminoMonteiroAdvogado.models import User
>>> User.query.all()  # Should return admin user

# 4. Deploy to GAE
gcloud app deploy --version=1

# 5. Verify production database
gcloud sql connect <instance-name> --user=postgres
```

---

## Quick Reference: Common AI Agent Tasks

### Task: Add a new editable text field to admin dashboard
```
1. Add ConteudoGeral entry in ensure_essential_data() with unique (pagina, secao)
2. In admin_routes.py dashboard(), pass content_for_page to template
3. In template, add <input> or <textarea> with name="content-{id}"
4. In update_content() route, parse request.form keys starting with "content-"
5. Update corresponding ConteudoGeral record and commit
```

### Task: Add a new service/practice area
```
1. Add AreaAtuacao record via admin or seed
2. ensure_essential_data() auto-creates Pagina with slug=area_slug
3. Add ConteudoGeral entries for that slug (titulo, descricao, etc.)
4. Template areas_atuacao/servico_base.html automatically receives content
5. URL /slug automatically routes via catch-all route
```

### Task: Fix broken image uploads
```
1. Check file extension against ALLOWED_EXTENSIONS in __init__.py
2. Verify UPLOAD_FOLDER path exists: static/images/uploads/
3. Check image_processor.py for PIL errors (import Image, etc.)
4. Ensure process_and_save_image() returns success=True
5. Verify database path stored relative to static/: images/uploads/filename.webp
```

### Task: Debug login failures
```
1. Verify User.query.all() returns admin user in flask shell
2. Check user.check_password(password) directly in shell
3. Ensure LoginForm includes {{ form.hidden_tag() }} in template
4. Check WTF_CSRF_ENABLED not false in config (unless testing)
5. Review Flask-Login @login_required decorators applied correctly
```

### Task: Add new page to navigation
```
1. Create Pagina record with slug, titulo_menu, template_path, show_in_menu=True
2. Create template at templates/{template_path}
3. Add ConteudoGeral entries for that slug if dynamic content needed
4. Template receives nav_pages automatically via context processor
5. Catch-all route /<path:slug> automatically handles navigation
```

### Task: Change site theme/colors
```
1. Edit ThemeSettings record (theme field and cor_primaria_tema*)
2. Update or create templates/home/home_option{N}.html with new design
3. Add CSS overrides in static/css/ or ConteudoGeral custom_css_overrides
4. Test all theme variants (option1-8) render without errors
5. Deploy with gcloud app deploy
```

---

## AI-Specific Guidance

1. **Before modifying templates**: Check if content is in `ConteudoGeral` table or hardcoded in Python—prefer database-backed content
2. **Before adding routes**: Verify it doesn't conflict with existing blueprints or dynamic `/<path:slug>` catch-all
3. **Database changes**: Always create migration via `flask db migrate` rather than manual DDL
4. **Form CSRF**: Ensure admin forms include `EmptyForm()` or explicit CSRF token for session integrity
5. **Image handling**: Use `process_and_save_image()` from `image_processor.py`; never store raw uploads
6. **Blueprint prefixes**: Auth uses `/auth` prefix (so login is `/auth/login`), admin is root (`/admin/`), main has no prefix
7. **ConteudoGeral querying**: Always filter by both `pagina` AND `secao` when searching for specific content
8. **Theme templates**: All theme files (option1-8) must extend appropriate base template; don't duplicate structure
9. **Migration rollbacks**: If a migration fails, use `flask db downgrade` then `flask db stamp head` before retrying

---

## Query Patterns & Best Practices

### ConteudoGeral Query Pattern (CRITICAL)
```python
# CORRECT: Filter by both pagina AND secao
content = ConteudoGeral.query.filter_by(pagina='home', secao='titulo').first()

# WRONG: Only filtering by secao is ambiguous across pages
content = ConteudoGeral.query.filter_by(secao='titulo').first()  # ❌ Bad!

# Batch loading for performance
all_home_content = ConteudoGeral.query.filter_by(pagina='home').all()
content_dict = {item.secao: item.conteudo for item in all_home_content}
```

### Pagina Navigation Queries
```python
# Get main menu pages (no parent, visible, active)
main_pages = Pagina.query.filter(
    Pagina.parent_id.is_(None),
    Pagina.show_in_menu == True,
    Pagina.ativo == True
).order_by(Pagina.ordem).all()

# Get child pages under parent
parent = Pagina.query.filter_by(slug='areas-de-atuacao').first()
services = parent.children  # Uses backref relationship

# Dynamic page lookup
page = Pagina.query.filter_by(slug=request_slug).first_or_404()
```

### AreaAtuacao & Related Content
```python
# Find service by slug
area = AreaAtuacao.query.filter_by(slug='direito-civil').first()

# Get all services ordered
services = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()

# Find related Pagina (auto-created with same slug)
page = Pagina.query.filter_by(slug=area.slug, tipo='servico').first()

# Fetch service-specific content
service_content = ConteudoGeral.query.filter_by(pagina=area.slug).all()
```

### HomePageSection Queries
```python
# Get all active sections in display order
sections = HomePageSection.query.filter_by(is_active=True).order_by(HomePageSection.order).all()

# Check if specific section type exists
hero = HomePageSection.query.filter_by(section_type='hero', is_active=True).first()
```

### User & Authentication Queries
```python
# Find user by username (login)
user = User.query.filter_by(username=form.username.data).first()

# Check password (use this, not verify_password!)
if user and user.check_password(password):
    login_user(user)

# Get current user in routes
@login_required
def protected_route():
    current_id = current_user.id  # From Flask-Login
```

---

## Common Gotchas & Anti-Patterns

### ❌ Anti-Pattern 1: Direct File Storage
**Wrong:**
```python
file.save(os.path.join(upload_folder, filename))  # No optimization!
```
**Right:**
```python
from ..image_processor import process_and_save_image
success, original_size, optimized_size, path = process_and_save_image(input_path, output_path)
```

### ❌ Anti-Pattern 2: Wrong Password Method
**Wrong:**
```python
if user.verify_password(password):  # Method doesn't exist!
```
**Right:**
```python
if user.check_password(password):  # Correct method from models.py
```

### ❌ Anti-Pattern 3: Ambiguous ConteudoGeral Queries
**Wrong:**
```python
title = ConteudoGeral.query.filter_by(secao='titulo').first().conteudo  # Which page?
```
**Right:**
```python
title = ConteudoGeral.query.filter_by(pagina='home', secao='titulo').first().conteudo
```

### ❌ Anti-Pattern 4: Missing CSRF in Admin Forms
**Wrong:**
```html
<form method="POST" action="/admin/update">
    <!-- Missing {{ form.hidden_tag() }} -->
    <input type="text" name="content">
</form>
```
**Right:**
```html
<form method="POST" action="/admin/update">
    {{ form.hidden_tag() }}  <!-- Includes CSRF token -->
    <input type="text" name="content">
</form>
```

### ❌ Anti-Pattern 5: Bypassing Migrations
**Wrong:**
```python
db.create_all()  # Only in development, breaks production!
```
**Right:**
```bash
flask db migrate -m "Add new column"
flask db upgrade
```

### ❌ Anti-Pattern 6: Hardcoding Database Values
**Wrong:**
```python
# In template or route
<h1>Belarmino Monteiro Advogado</h1>  # Hardcoded!
```
**Right:**
```python
# In database (ConteudoGeral)
titulo = ConteudoGeral.query.filter_by(pagina='home', secao='titulo').first().conteudo
# In template
<h1>{{ titulo }}</h1>
```

### ❌ Anti-Pattern 7: Circular Import Issues
**Wrong:**
```python
# In models.py
from .routes import main_bp  # Circular!
```
**Right:**
```python
# Keep models.py import-clean; do late imports in create_app()
```

### ⚠️ Gotcha 1: Theme Template Selection
The `home()` route in `main_routes.py` dynamically selects the template:
```python
theme = ThemeSettings.query.first().theme  # e.g., 'option4'
template_name = f'home/home_{theme}.html'  # Looks for home/home_option4.html
```
If the template doesn't exist, Flask will raise a `TemplateNotFound` error. Always create the template file first.

### ⚠️ Gotcha 2: Event Listener Timing
SQLAlchemy event listeners on `before_update` run BEFORE the commit:
```python
@event.listens_for(ConteudoGeral, 'before_update')
def receive_before_update(mapper, connection, target):
    pagina = Pagina.query.filter_by(slug=target.pagina).first()
    if pagina: pagina.data_modificacao = datetime.utcnow()  # In same transaction
```
The `data_modificacao` update is included in the same `db.session.commit()` call.

### ⚠️ Gotcha 3: ConteudoGeral Default Values
If a `ConteudoGeral` entry doesn't exist, you'll get `None`. Always check:
```python
content = ConteudoGeral.query.filter_by(pagina='home', secao='titulo').first()
title = content.conteudo if content else "Default Title"
```

### ⚠️ Gotcha 4: Upload Folder Doesn't Auto-Create
The `static/images/uploads/` folder must exist or file saves will fail. Code checks and creates it:
```python
upload_folder = current_app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)  # Creates if missing
```

### ⚠️ Gotcha 5: TESTING Mode Disables CSRF
In `test_app.py`, CSRF is disabled for convenience:
```python
app.config['WTF_CSRF_ENABLED'] = False
```
Production and local dev MUST have CSRF enabled. Test fixtures are special cases.

---

## File Organization & Directory Structure

### Source Code Layout
```
BelarminoMonteiroAdvogado/
├── __init__.py                 # App factory, ensure_essential_data(), render_page()
├── models.py                   # SQLAlchemy models (Pagina, ConteudoGeral, AreaAtuacao, etc.)
├── forms.py                    # WTForms (LoginForm, ChangePasswordForm, ContactForm, etc.)
├── image_processor.py          # Image optimization to WebP with PIL
├── routes/
│   ├── __init__.py             # Blueprint imports and registration
│   ├── main_routes.py          # Public routes (/, /areas-de-atuacao, /<path:slug>)
│   ├── auth_routes.py          # Auth routes (/auth/login, /auth/logout with /auth prefix)
│   └── admin_routes.py         # Admin routes (/admin/dashboard, /admin/update-content)
├── static/
│   ├── css/                    # Stylesheets (style.css, themes, etc.)
│   ├── js/                     # JavaScript files
│   ├── images/                 # Static images
│   │   └── uploads/            # User-uploaded files (created on-demand, writable)
│   ├── videos/                 # Video assets
│   └── service-worker.js       # PWA service worker
└── templates/
    ├── base.html               # Main layout template
    ├── base_option[1-8].html   # Theme-specific base templates
    ├── home/
    │   ├── index.html          # Home page handler (generic)
    │   └── home_option[1-8].html # Theme-specific home templates
    ├── admin/
    │   ├── dashboard.html      # Main admin dashboard (unified UI)
    │   └── login.html          # Admin login page
    ├── auth/
    │   └── login.html          # (Note: also at /auth/login route)
    ├── areas_atuacao/
    │   ├── todas_areas.html    # List all services
    │   └── servico_base.html   # Individual service detail (auto-rendered for each slug)
    ├── contato/
    │   └── contato.html        # Contact form page
    ├── _*.html                 # Partial templates (navigation, filters, scripts, etc.)
    ├── 404.html / 500.html     # Error pages
    └── robots.txt / sitemap.xml # SEO files

instance/
├── site.db                     # SQLite database (local dev only)
└── backups/                    # Database backups

migrations/
├── alembic.ini                 # Alembic configuration
├── env.py                      # Migration environment setup
├── script.py.mako              # Migration template
└── versions/                   # Migration files (auto-generated by flask db migrate)
```

### Key Configuration Files
- `app.yaml`: Google App Engine deployment config (Gunicorn, scaling, handlers)
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (loaded by python-dotenv)
- `run.ps1`: PowerShell script for local dev startup (Windows)
- `auto_fix.py`: Database initialization and consistency checks

### Template Variable Naming Conventions
Templates reference `ConteudoGeral` entries by their `secao` name:
- `{{ titulo }}` → ConteudoGeral where `secao='titulo'`
- `{{ paragrafo }}` → ConteudoGeral where `secao='paragrafo'`
- `{{ hero_show_button }}` → ConteudoGeral where `secao='hero_show_button'` and `field_type='boolean'`
- `{{ google_analytics_config|from_json_filter }}` → ConteudoGeral where `field_type='json'`

---

## Complete Project Script Ecosystem Overview

### Workflow: Development → Testing → Deployment

```
┌─ LOCAL DEVELOPMENT ─────────────────────────────────────────┐
│                                                               │
│  Start: .\run.ps1                                            │
│    ↓                                                          │
│  ├─ venv activation                                          │
│  ├─ pip install -r requirements.txt                          │
│  ├─ auto_fix.py (database consistency)                       │
│  ├─ flask db upgrade (migrations)                            │
│  ├─ flask init-db (ensure_essential_data)                    │
│  └─ Flask dev server (http://127.0.0.1:5000)               │
│                                                               │
│  Clean Reset: .\run.ps1 clean                                │
│    ├─ Removes site.db                                        │
│    ├─ Removes migrations/                                    │
│    └─ Rebuilds from scratch                                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─ TESTING ──────────────────────────────────────────────────┐
│                                                              │
│  Quick Test: pytest test_app.py                             │
│  All Tests:  python run_all_tests.py (master runner)        │
│                                                              │
│  Test Coverage:                                             │
│  ├─ test_app.py (fixtures, basic routes)                   │
│  ├─ test_admin_routes.py (admin functionality)              │
│  ├─ test_all_routes_complete.py (all public routes)         │
│  ├─ test_all_themes_complete.py (8 theme variants)          │
│  └─ test_producao_completo.py (production readiness)        │
│                                                              │
│  Database Check: python check_db.py                         │
│  Diagnostics:   python diagnostico.py                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌─ PRE-DEPLOYMENT ───────────────────────────────────────────┐
│                                                              │
│  1. python validar_deploy.py (validate current state)       │
│  2. python run_all_tests.py (run all tests)                │
│  3. python otimizar_imagens.py (optimize media)             │
│  4. python backup_db.py (backup database)                   │
│  5. git status / git commit (version control)               │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌─ DEPLOYMENT ───────────────────────────────────────────────┐
│                                                              │
│  GAE:          gcloud app deploy                            │
│  PythonAnywhere: python deploy_pythonanywhere_auto.py       │
│  Custom:       python deploy_production_complete.py         │
│                                                              │
│  Post-Deploy:  python validar_deploy.py (verify)           │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌─ MAINTENANCE ──────────────────────────────────────────────┐
│                                                              │
│  Database Maintenance:                                      │
│  ├─ Backup:    python backup_db.py                         │
│  ├─ Check:     python check_db.py                          │
│  ├─ Repair:    python repair_alembic.py                    │
│                                                              │
│  Image Optimization:                                        │
│  ├─ Batch:     python otimizar_imagens.py                  │
│                                                              │
│  Cleanup:                                                   │
│  ├─ Project:   python limpar_projeto.py                    │
│  ├─ Venv:      python limpeza_total_venv.py                │
│                                                              │
│  Diagnostics:                                               │
│  ├─ General:   python diagnostico.py                       │
│  ├─ Video:     python diagnostico_video_completo.py        │
│  ├─ Git:       python verificar_versao_github.py           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Script Dependencies & Execution Order

### Startup Sequence (run.ps1)
```
1. Activate venv
2. Install pip packages
3. Execute auto_fix.py (repairs migrations, creates backups)
4. Flask init-db (ensures essential data exists)
5. Start dev server
```

### Pre-Deployment Sequence
```
1. python validar_deploy.py (checks current state)
2. python run_all_tests.py (comprehensive testing)
3. python otimizar_imagens.py (media optimization)
4. python backup_db.py (database backup)
5. gcloud app deploy or python deploy_production_complete.py
6. python validar_deploy.py (post-deploy verification)
```

### Common Troubleshooting Sequences

**Database corrupted:**
```
1. python backup_db.py --remove-migrations
2. Delete instance/site.db if it exists
3. .\run.ps1 clean
4. .\run.ps1 (restart)
```

**Migrations broken:**
```
1. python repair_alembic.py
2. flask db stamp head
3. flask db migrate -m "recovery"
4. flask db upgrade
```

**Admin locked out:**
```
1. python check_db.py (verify DB accessible)
2. python create_admin.py (create new admin)
```

**Deployment validation:**
```
1. python diagnostico.py (system health)
2. python validar_deploy.py (deployment readiness)
3. python test_producao_completo.py (production tests)
```

---

## Environment Configuration

### Local Development (.env)
```
FLASK_ENV=development
FLASK_APP=BelarminoMonteiroAdvogado
DATABASE_URL=sqlite:///instance/site.db
```

### Production (GAE / app.yaml)
```
runtime: python311
entrypoint: gunicorn -b :$PORT main:app
env_variables:
  FLASK_ENV: production
  DATABASE_URL: postgresql://... (if using Cloud SQL)
  SECRET_KEY: <generated-secret>
```

### Database Paths
- **Local Dev**: `instance/site.db` (SQLite)
- **Testing**: In-memory SQLite (`:memory:`)
- **Production**: Environment variable `DATABASE_URL` (PostgreSQL recommended)

---

## Performance Optimization Tips

### Image Handling
- Use `otimizar_imagens.py` to batch convert to WebP
- Quality setting: 95% (imperceptible visual loss)
- Max width: 2560px (responsive scaling)
- Result: ~70% file size reduction typically

### Database Queries
- Always filter `ConteudoGeral` by **both** `pagina` AND `secao`
- Batch load related content instead of N+1 queries
- Use `joinedload()` for relationships in context processors
- Index frequently-queried fields (already configured: `slug`, `ativo`, `tipo`)

### Template Rendering
- Use `{{ get_file_mtime('css/style.css') }}` for cache busting
- Use `from_json_filter` for JSON configuration in templates
- Leverage context processors for global data

### Caching
- GAE app.yaml sets 1-day cache for `/static` files
- Use versioning (`?v=timestamp`) for dynamic assets
- CloudFlare/CDN recommended for production

---

Quick navigation to key sections:

| Section | Use When | Key Details |
|---------|----------|------------|
| **Project Overview** | Need big-picture understanding | Architecture, tech stack, design philosophy |
| **Critical Developer Workflows** | Getting started or debugging | Setup (run.ps1), migrations, testing |
| **Architecture Patterns** | Building new features | Content model, blueprints, themes, images |
| **Project-Specific Conventions** | Writing code | Forms, CSRF, config, event listeners, filters |
| **Data Models Deep Dive** | Understanding relationships | Pagina, ConteudoGeral, AreaAtuacao, etc. |
| **Content Flow** | Debugging rendering issues | Database → render_page() → template |
| **App Initialization** | Understanding startup | create_app(), blueprint registration |
| **Admin Routes Deep Dive** | Building admin features | Dashboard, content update, form handling |
| **Authentication Routes Deep Dive** | Login/security issues | Login flow, password checking, redirects |
| **Template Structure** | Creating/modifying templates | Base hierarchy, variables, inheritance |
| **Common Debugging Scenarios** | Troubleshooting | Database, images, login, migrations |
| **Testing Guidance** | Writing tests | Fixtures, CSRF, patterns |
| **Email Configuration** | Contact form or notifications | SMTP setup, Gmail app passwords |
| **Deployment Notes** | Going to production | GAE config, databases, static files |
| **Query Patterns** | Writing database code | ConteudoGeral, Pagina, relationships |
| **Common Gotchas** | Avoiding bugs | Anti-patterns, timing issues, gotchas |
| **File Organization** | Finding code | Directory structure, templates layout |
| **Quick Reference** | Common tasks | 6 step-by-step AI agent workflows |

---

## Utility Scripts Reference

### Database Management Scripts

#### `auto_fix.py` (432 lines) - CRITICAL
**Purpose**: Automated database and environment maintenance during app startup
**Functions**:
- Sets up logging to `run_log.txt`
- Ensures `instance/` folder exists
- Backs up SQLite database to `instance/backups/`
- Repairs Alembic migration inconsistencies
- Detects and fixes `alembic_version` table corruption
- Creates baseline migrations if needed
- Validates migration state before app starts

**When to use**: Part of `run.ps1` startup flow - runs automatically
```powershell
# Manually if needed:
python auto_fix.py
```

#### `check_db.py` (56 lines) - Diagnostic
**Purpose**: Verify SQLite database integrity and accessibility
**Functions**:
- Connects to `instance/site.db`
- Lists all tables
- Tests access to `user` table
- Reports connection status

**When to use**: Troubleshoot database access issues
```powershell
python check_db.py
```

#### `backup_db.py` (78 lines) - Maintenance
**Purpose**: Create timestamped backups of SQLite database
**Functions**:
- Creates backup in `instance/backups/` with timestamp
- Optionally removes original database
- Optionally removes migrations folder (for clean reset)

**When to use**: Before major schema changes or database reset
```powershell
# Backup only
python backup_db.py

# Backup and remove migrations for clean reset
python backup_db.py --remove-migrations
```

#### `repair_alembic.py` - Migration Recovery
**Purpose**: Repair broken Alembic/migration state
**When to use**: If migrations fail with "Can't locate revision" errors
```powershell
python repair_alembic.py
```

### Admin/Creation Scripts

#### `create_admin.py` (100 lines) - User Management
**Purpose**: Create or reset admin user from command line
**Functions**:
- Prompts for username, email, password
- Locates `create_app()` factory automatically
- Imports `User` and `db` models
- Adds user to database

**When to use**: Create initial admin or reset lost password
```powershell
python create_admin.py
# Prompts:
# Admin username: admin
# Admin email (optional): admin@example.com
# Admin password: (hidden input)
```

### Testing Scripts

#### `test_app.py` (54 lines) - Core Unit Tests
**Purpose**: Foundational test suite with fixtures
**Tests**:
- Login page loads
- Successful login with valid credentials
- Service creation in admin

**Run**:
```powershell
pytest test_app.py -v
pytest test_app.py::test_login_success -v
```

#### `run_all_tests.py` (193 lines) - Master Test Runner
**Purpose**: Execute ALL test files and generate comprehensive report
**Functions**:
- Discovers all test files
- Runs with 60-second timeout per file
- Generates HTML report
- Blocks deployment if critical tests fail
- Color-coded output (green/red/yellow)

**Run**:
```powershell
python run_all_tests.py
```

**Test files discovered**:
- `test_admin_routes.py`
- `test_all_routes_complete.py`
- `test_all_themes.py`
- `test_all_themes_complete.py`
- `test_completo_final.py`
- `test_database_schema.py`
- `test_links_rotas_completo.py`
- `test_media_completo.py`
- `test_pre_deploy_completo.py`
- `test_producao_completo.py`
- `test_visual_humano_completo.py`

#### `test_admin_routes.py` - Admin Route Tests
Tests all admin dashboard routes, content updates, form handling

#### `test_all_routes_complete.py` - Route Coverage
Tests all public routes, error pages, redirects, and edge cases

#### `test_all_themes_complete.py` - Theme Testing
Tests all 8 theme variants (option1-8) rendering without errors

### Image & Media Scripts

#### `otimizar_imagens.py` (261 lines) - Image Optimization
**Purpose**: Batch convert and optimize ALL images to WebP
**Features**:
- Converts JPG, PNG, GIF, BMP, TIFF → WebP
- Quality: 95% (imperceptible loss)
- Intelligent resizing (max 2560px width)
- Maintains aspect ratio
- Creates backups of originals
- Supports batch processing

**Run**:
```powershell
python otimizar_imagens.py
```

**Output**: 
- `static/images/uploads/*.webp`
- `instance/backups/images_backup_TIMESTAMP/`

### SEO & Theme Fixes

#### `fix_seo_all_themes.py` - SEO Meta Tags
Adds/fixes meta tags (title, description, keywords) for all theme variants

#### `diagnose_themes_5678.py` - Theme Diagnostics
Diagnoses rendering issues in theme options 5-8

#### `fix_missing_images.py` - Media Validation
Scans templates for broken image references, suggests fixes

#### `fix_all_contrast_issues.py` - Accessibility
Checks color contrast ratios, fixes A11y violations

#### `fix_video_posicionamento_final.py` - Video Layout
Fixes video positioning in home page sections

### Deployment Scripts

#### `deploy_pythonanywhere_auto.py` - PythonAnywhere Deployment
Automated deployment to PythonAnywhere hosting
- Uploads via SFTP
- Reloads web app
- Runs migrations
- Logs output

**Run**:
```powershell
python deploy_pythonanywhere_auto.py
```

#### `deploy_production_complete.py` - Production Deploy
Complete production deployment workflow:
- Runs all tests first
- Creates database backup
- Performs migrations
- Updates static files
- Validates deployment

**Run**:
```powershell
python deploy_production_complete.py
```

#### `validar_deploy.py` - Deployment Validation
Post-deployment verification:
- Checks all routes respond
- Validates database connectivity
- Tests admin functionality
- Verifies static files served

**Run**:
```powershell
python validar_deploy.py
```

### Cleanup & Repository Scripts

#### `limpar_projeto.py` - Project Cleanup
Removes temporary files, cache, backups
- Deletes `__pycache__` folders
- Removes `.pyc` files
- Clears old backups
- Resets logs

**Run**:
```powershell
python limpar_projeto.py
```

#### `limpeza_total_venv.py` - Virtual Environment Reset
Complete venv cleanup and rebuild
- Removes entire `venv/` folder
- Reinstalls all dependencies
- Fresh start

**Warning**: This is destructive! Back up first.

#### `criar_repo_github.py` - Repository Initialization
Creates/initializes GitHub repository structure

#### `criar_repo_limpo.py` - Clean Repository Creation
Creates clean clone without development artifacts

#### `criar_zip_limpo.py` - Distribution Archive
Creates clean `.zip` archive for distribution (no venv, cache, etc.)

### Diagnostic Scripts

#### `diagnostico.py` - General Diagnostics
Comprehensive system health check:
- Python version
- Installed packages
- Database status
- Flask app loads correctly
- Routes accessible

**Run**:
```powershell
python diagnostico.py
```

#### `diagnostico_video_completo.py` - Video/Media Diagnostics
Tests video embedding, formats, loading

#### `verificar_versao_github.py` - Git Status Check
Shows git branch, uncommitted changes, sync status

---

## Useful Commands for Debugging

```powershell
# Check Python environment
python --version
pip list

# Run specific test
pytest test_app.py::test_login_success -v

# Run all tests with master runner
python run_all_tests.py

# Access Flask shell (with app context)
flask shell

# Check migrations status
flask db current
flask db heads

# Database inspection (from Flask shell)
>>> from BelarminoMonteiroAdvogado.models import *
>>> Pagina.query.all()

# Check database integrity
python check_db.py

# Backup before major changes
python backup_db.py

# Optimize images
python otimizar_imagens.py

# Run diagnostics
python diagnostico.py

# Clean project
python limpar_projeto.py
```

---

## Security & Environment Variables

**Secret Detection**: This project uses `detect-secrets` (installed via `requirements.txt`) via a pre-commit hook to prevent committing API keys or passwords. Any new potential secret will block the commit. Legitimate but flagged strings should be added to the `.secrets.baseline` file.

### Critical Security Settings

**Do NOT commit to repository:**
```
- .env file (contains SECRET_KEY, database credentials)
- instance/site.db (local development database)
- migrations/ folder generated locally
- __pycache__ directories
- test_uploads/ directory
```

**Use `.gitignore` to prevent accidental commits:**
```
.env
instance/site.db
instance/backups/
migrations/versions/*.py
__pycache__/
*.pyc
test_uploads/
venv/
.DS_Store
```

### Secret Key Generation
```python
# Generate strong SECRET_KEY for production
import secrets
print(secrets.token_hex(32))  # 64-character hex string

# Store in GAE environment or .env (local dev only)
```

### Database Security
- **Local**: SQLite acceptable for development
- **Production**: Use PostgreSQL with strong credentials
- **Credentials**: Store in environment variables, NEVER in code
- **Backups**: Use `backup_db.py` before major changes

### Form Security
- All admin forms require CSRF token via `EmptyForm()`
- Flask-WTF handles CSRF automatically
- Test mode disables CSRF (`WTF_CSRF_ENABLED=False`)

### Password Security
- Passwords hashed with `werkzeug.security.generate_password_hash()`
- Always use `user.check_password()` to verify
- Never store plaintext passwords

### File Upload Security
- Validate file extensions against `ALLOWED_EXTENSIONS`
- Use `secure_filename()` from Werkzeug
- Generate unique filenames with `secrets.token_hex()`
- Store paths relative to `static/` for portability

---

## Deployment Strategies

### Strategy 1: Google App Engine (Recommended)
**Pros**: Scalable, managed, global CDN
**Setup**:
1. Create Google Cloud project
2. Enable App Engine, Cloud SQL
3. Configure `app.yaml` with environment variables
4. Run: `gcloud app deploy`

**Post-Deploy**:
```bash
gcloud app logs read
gcloud sql connect <instance-name> --user=postgres
```

### Strategy 2: PythonAnywhere
**Pros**: Simple, Python-focused, good for learning
**Setup**:
1. Create PythonAnywhere account
2. Configure WSGI file
3. Set environment variables in web app settings
4. Run: `python deploy_pythonanywhere_auto.py`

### Strategy 3: Self-Hosted (Docker/VPS)
**Requirements**:
- Python 3.11+
- PostgreSQL or MySQL
- Reverse proxy (Nginx/Apache)
- Process manager (Gunicorn/uWSGI)

**Steps**:
```bash
git clone <repo>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
gunicorn -w 4 main:app
```

---

## Troubleshooting Decision Tree

```
Problem: App won't start
├─ Check Python version: python --version (need 3.11+)
├─ Check venv: Activate and pip list
├─ Check dependencies: pip install -r requirements.txt
├─ Check auto_fix.py: python auto_fix.py
└─ Check database: python check_db.py

Problem: Database error
├─ Check database exists: python check_db.py
├─ Check migrations: flask db current
├─ Repair migrations: python repair_alembic.py
└─ Reset database: .\run.ps1 clean

Problem: Login not working
├─ Check admin user: flask shell → User.query.all()
├─ Create admin: python create_admin.py
├─ Check password: user.check_password('password')
└─ Check CSRF: form.hidden_tag() in template

Problem: Images not optimized
├─ Check PIL installed: pip install Pillow
├─ Run optimizer: python otimizar_imagens.py
├─ Check uploads folder: ls static/images/uploads/
└─ Verify paths in database: Check ConteudoGeral.conteudo

Problem: Template not rendering
├─ Check template exists: ls templates/{path}
├─ Check content exists: ConteudoGeral.query.filter_by(...)
├─ Check context: Print render_page() output
└─ Check variables: {{ variable }} in template

Problem: Deploy failing
├─ Run all tests: python run_all_tests.py
├─ Backup database: python backup_db.py
├─ Check migrations: flask db upgrade
├─ Validate deployment: python validar_deploy.py
└─ Check app.yaml: Verify environment variables
```

---

## 🎯 Complete Python Scripts Ecosystem Reference

### 📋 Master Script (Entry Point)

#### `run.ps1` - PowerShell Master Orchestrator
**Role**: Entry point for ALL local development  
**What it does**:
1. Activates virtual environment  
2. Upgrades pip  
3. Installs requirements  
4. Creates `instance/` folder  
5. Runs `auto_fix.py` (database consistency)  
6. Runs `flask init-db` (populate essential data)  
7. Starts Flask dev server on `http://127.0.0.1:5000`

**Usage**:
```powershell
.\run.ps1              # Standard start
.\run.ps1 clean        # Reset DB and migrations completely
```

**📌 AI REMINDER**: This is the ONLY recommended way to start development. Never run `flask run` directly.

---

### 🔧 Database & Environment Management

#### `auto_fix.py` (432 lines) - CRITICAL
**Execution**: Automatic (called by `run.ps1` EVERY startup)  
**Purpose**: Ensure database is in consistent state  

**Functionality**:
- ✅ Logs all operations to `run_log.txt` with timestamps
- ✅ Creates `instance/` folder if missing
- ✅ Backs up current `site.db` to `instance/backups/`
- ✅ Detects and repairs Alembic migration corruption
- ✅ Fixes broken `alembic_version` table
- ✅ Creates baseline migrations if needed
- ✅ Validates migration state before app starts
- ✅ Wraps shell commands with error handling

**Key Code Patterns**:
```python
log_operation(msg)              # Logs to file + console
run_shell_command(cmd)          # Shell execution with logging
backup_database()               # Timestamped backup
repair_alembic_version()        # Fixes corruption
check_migrations_state()        # Validates status
```

**When to use manually**:
```powershell
python auto_fix.py              # If run.ps1 fails
```

**⚠️ Critical**: Check `run_log.txt` output. If errors appear, investigate before proceeding.

**Relationship Map**:
- Called BY: `run.ps1` (always, first)
- Calls: Flask db commands
- Precedes: `flask init-db`
- Generates: `run_log.txt` (full trace)
- Uses: `check_db.py` logic internally

---

#### `check_db.py` (56 lines) - Database Diagnostics
**Purpose**: Quick integrity check of SQLite database  
**Speed**: ~10 seconds

**What it checks**:
- Database connectivity
- Table count and list
- `user` table accessibility
- General database health

**Usage**:
```powershell
python check_db.py
```

**Example output**:
```
✓ Connected to SQLite: instance/site.db
✓ Tables: 12 found
✓ User table: Accessible
✓ Status: Database OK
```

**When to use**:
- After database errors in logs
- Before deployment
- When `run.ps1` fails at DB stage
- Regular health checks

**Relationship Map**:
- Used BY: Developers, CI/CD
- Calls: SQLAlchemy models
- Precedes: `repair_alembic.py` (if needed)

---

#### `backup_db.py` (78 lines) - Database Backup
**Purpose**: Create timestamped backups before destructive operations  
**Speed**: ~30 seconds

**What it does**:
- Creates backup in `instance/backups/` with timestamp (YYYY-MM-DD_HH-MM-SS)
- Optionally removes original `site.db` after backup
- Optionally removes `migrations/` folder for clean reset
- Reports sizes

**Usage**:
```powershell
python backup_db.py                          # Backup only
python backup_db.py --remove-migrations      # Backup + reset migrations
```

**When to use**:
- Before running `repair_alembic.py`
- Before major schema changes
- Before deployment
- **ALWAYS before destructive operations**

**⚠️ WARNING**: `--remove-migrations` is destructive!

**Relationship Map**:
- Called BY: Developers, `deploy_production_complete.py`
- Creates: Timestamped backup
- Precedes: `repair_alembic.py`, deployment scripts

---

#### `repair_alembic.py` - Migration Recovery
**Purpose**: Fix broken Alembic/migration state  
**When needed**: "Can't locate revision identified by..." errors

**Recovery workflow**:
```powershell
python backup_db.py          # Step 1: Backup FIRST
python repair_alembic.py     # Step 2: Repair migrations
flask db migrate -m "recovery"  # Step 3: Create recovery migration
flask db upgrade             # Step 4: Apply it
```

**Relationship Map**:
- Uses: `auto_fix.py` functions internally
- Called after: Database corruption detected
- Precedes: `validar_deploy.py`

---

#### `create_admin.py` (100 lines) - Admin User Management
**Purpose**: Create/reset admin user without database GUI  
**Speed**: ~1 minute

**Functionality**:
- Interactive prompts for username, email, password
- Auto-locates `create_app()` factory
- Dynamically imports `User` and `db` models
- Adds user with hashed password
- Supports multiple admins

**Usage**:
```powershell
python create_admin.py

# Prompts appear:
# Admin username: admin
# Admin email (optional): admin@example.com
# Admin password: (hidden input)
```

**When to use**:
- After database reset
- When adding additional admins
- When admin password is lost
- During first-time setup

**Relationship Map**:
- Uses: User model, password hashing
- Called during: `flask init-db` (automatic)
- Precedes: Login testing

---

### 🧪 Testing & Validation Scripts

#### `test_app.py` (54 lines) - Core Unit Tests
**Framework**: pytest  
**Database**: In-memory SQLite  
**CSRF**: Disabled for tests

**Test fixtures provided**:
- `app`: Flask test app with test config
- `client`: Flask test client

**Tests included**:
- Login page loads (GET)
- Login success with valid credentials
- Admin dashboard access
- Service creation

**Usage**:
```powershell
pytest test_app.py -v                    # All tests
pytest test_app.py::test_login_success   # Specific test
pytest test_app.py -k login              # Pattern matching
```

**Config details**:
```python
TESTING=True
SQLALCHEMY_DATABASE_URI=sqlite:///:memory:
WTF_CSRF_ENABLED=False
```

**📌 Admin credentials for tests**: `admin/admin` (fixture-only)

---

#### `run_all_tests.py` (193 lines) - Master Test Runner
**Purpose**: Run EVERY test file and generate report  
**Speed**: 15-20 seconds total  
**Blocking**: STOPS deployment if critical tests fail

**Discovers & runs**:
1. `test_app.py` - Core fixtures
2. `test_admin_routes.py` - Admin functionality
3. `test_all_routes_complete.py` - All public routes
4. `test_all_themes_complete.py` - 8 theme variants
5. `test_database_schema.py` - Schema validation
6. `test_producao_completo.py` - Production readiness
7. `test_pre_deploy_completo.py` - Pre-deployment
8. `test_links_rotas_completo.py` - Link validation
9. `test_media_completo.py` - Media/image tests
10. `test_completo_final.py` - Final integration
11. `test_human_simulation.py` - User behavior
12. `test_visual_humano_completo.py` - Visual rendering

**Usage**:
```powershell
python run_all_tests.py      # Run all tests
```

**Output format**:
```
Running: test_app.py ... PASS (0.45s)
Running: test_admin_routes.py ... PASS (1.23s)
Running: test_all_themes_complete.py ... PASS (2.15s)
...
✓ All tests passed (12 files, 127 tests, 15.8s)
```

**Relationship Map**:
- Calls: All individual test_*.py files
- Precedes: `deploy_production_complete.py`
- Used BY: CI/CD pipelines, deployment scripts

**📌 AI REMINDER**: NEVER deploy without running this first!

---

### 🚀 Deployment & Validation Scripts

#### `validar_deploy.py` - Deployment Validator
**Purpose**: Post-deployment verification  
**Speed**: 2-3 minutes

**Checks performed**:
- ✅ All routes respond (200 status)
- ✅ Database connectivity
- ✅ Admin functionality
- ✅ Static files served
- ✅ Environment variables set
- ✅ Error pages (404, 500) accessible

**Usage**:
```powershell
python validar_deploy.py     # Verify current deployment
```

**When to use**:
- After `gcloud app deploy`
- After PythonAnywhere upload
- Before marking deployment complete
- When deployment seems broken

**Relationship Map**:
- Called after: Any deployment
- Depends on: `run_all_tests.py` passing first
- Precedes: Team notification

---

#### `deploy_production_complete.py` - Full Production Deployment
**Purpose**: Complete end-to-end production deployment workflow  
**Speed**: 5-10 minutes

**Workflow**:
1. Runs `run_all_tests.py`
2. Creates database backup
3. Performs migrations
4. Updates static files
5. Calls `validar_deploy.py` at end
6. Reports status

**Usage**:
```powershell
python deploy_production_complete.py
```

**Relationship Map**:
- Uses: `run_all_tests.py`, `backup_db.py`
- Calls: `validar_deploy.py` at end
- Replaces: Manual deployment steps

---

#### `deploy_pythonanywhere_auto.py` - PythonAnywhere Deploy
**Purpose**: Automated PythonAnywhere hosting deployment  

**Features**:
- SFTP upload to PythonAnywhere server
- Web app reload
- Migrations execution
- Output logging

**Configuration needed**:
- PythonAnywhere API token
- Username and domain

**Usage**:
```powershell
python deploy_pythonanywhere_auto.py
```

**Relationship Map**:
- Alternative to: `deploy_production_complete.py` (for GAE)
- Uses: Same database migrations
- Precedes: `validar_deploy.py`

---

### 🎨 Content & Media Management Scripts

#### `otimizar_imagens.py` (261 lines) - Image Optimization
**Purpose**: Batch convert and optimize ALL images to WebP  
**Speed**: 5-30 minutes (depends on image count)  
**Result**: ~70% file size reduction

**Features**:
- Converts: JPG, PNG, GIF, BMP, TIFF → WebP
- Quality: 95% (imperceptible loss)
- Resizing: Intelligent (max 2560px width)
- Maintains: Aspect ratio
- Creates: Backups of originals
- Supports: Batch processing

**Usage**:
```powershell
python otimizar_imagens.py
```

**Output**:
- `static/images/uploads/*.webp` (optimized files)
- `instance/backups/images_backup_TIMESTAMP/` (original backups)

**When to use**:
- Before first deployment
- When adding many images
- Pre-production optimization
- Regular maintenance (monthly)

**Relationship Map**:
- Works with: `image_processor.py` (in app code)
- Part of: `deploy_production_complete.py`
- Reduces: Deployment bandwidth

**📌 AI REMINDER**: Run before GAE deployment to reduce costs.

---

#### `fix_seo_all_themes.py` - SEO Meta Tags
**Purpose**: Add/fix meta tags for all theme variants  

**Updates**:
- Title, description, keywords
- Open Graph tags
- Structured data
- All 8 theme options

**Usage**:
```powershell
python fix_seo_all_themes.py
```

---

#### `fix_missing_images.py` - Image Validation
**Purpose**: Scan for broken image references  

**Reports**:
- Missing images
- Broken paths
- Dead links
- Suggested fixes

**Usage**:
```powershell
python fix_missing_images.py
```

---

#### `fix_all_contrast_issues.py` - Accessibility Fix
**Purpose**: WCAG AA color contrast compliance  

**Checks**:
- Contrast ratios
- A11y compliance
- Color suggestions
- Accessibility score

**Usage**:
```powershell
python fix_all_contrast_issues.py
```

---

#### `fix_video_posicionamento_final.py` - Video Layout
**Purpose**: Fix video positioning in home page  

**Usage**:
```powershell
python fix_video_posicionamento_final.py
```

---

### 🔧 Diagnostic & Utility Scripts

#### `diagnostico.py` - System Health Check
**Purpose**: Comprehensive system diagnostics  
**Speed**: 1-2 minutes

**Checks**:
- Python version and path
- Installed packages/versions
- Database status
- Flask app loads
- Routes count
- Templates render
- Static files served

**Usage**:
```powershell
python diagnostico.py
```

**Output example**:
```
Python 3.11.4 ✓
Database: instance/site.db ✓
Flask app: OK ✓
Routes: 47 found ✓
Migrations: Up-to-date ✓
```

**When to use**:
- Initial setup verification
- Troubleshooting issues
- Pre-deployment checks
- Environment validation

**Relationship Map**:
- Calls: `check_db.py` logic
- Precedes: `validar_deploy.py`

---

#### `diagnostico_video_completo.py` - Media Diagnostics
**Purpose**: Test video embedding, formats, loading  

**Checks**:
- Video file formats (mp4, webm)
- Codec support
- Template embedding
- CDN loading
- Stream integrity

**Usage**:
```powershell
python diagnostico_video_completo.py
```

---

#### `verificar_versao_github.py` - Git Status
**Purpose**: Show git branch, changes, sync status  
**Speed**: ~10 seconds

**Information**:
- Current branch
- Uncommitted changes
- Remote sync status
- Commit count

**Usage**:
```powershell
python verificar_versao_github.py
```

**Output example**:
```
Current Branch: main
Changes: 3 uncommitted
Ahead: 2 commits
Status: Ready to push
```

---

### 🧹 Cleanup & Repository Scripts

#### `limpar_projeto.py` - Project Cleanup
**Purpose**: Remove temporary files and cache  

**Removes**:
- `__pycache__` folders
- `.pyc` files
- Old backups
- Logs
- Temp files

**Usage**:
```powershell
python limpar_projeto.py
```

**When to use**:
- Before committing to git
- Regular maintenance
- Reduce repository size

---

#### `limpeza_total_venv.py` - Venv Reset
**Purpose**: Complete virtual environment rebuild  
**Speed**: 5-10 minutes

**Actions**:
- Removes entire `venv/` folder
- Reinstalls all dependencies
- Fresh start

**⚠️ DESTRUCTIVE**: Backup first!

**Usage**:
```powershell
python limpeza_total_venv.py
```

**When to use**:
- Venv corrupted
- Before Python version update
- Emergency recovery

---

#### `criar_zip_limpo.py` - Distribution Archive
**Purpose**: Create clean `.zip` for distribution  

**Excludes**:
- venv/
- __pycache__/
- .pyc files
- Instance data
- Dev artifacts

**Usage**:
```powershell
python criar_zip_limpo.py
```

**Output**: `BMA_VF_clean_YYYY-MM-DD.zip`

---

#### `criar_repo_github.py` & `criar_repo_limpo.py` - Repository Setup
**Purpose**: Initialize repository structure  

**Functions**:
- Create folder structure
- Setup .gitignore
- Initialize git
- Push to GitHub

**Usage**:
```powershell
python criar_repo_limpo.py       # Local
python criar_repo_github.py      # GitHub
```

---

## 🔄 Script Dependency & Execution Flow

### Local Development Startup Flow
```
.\run.ps1
  ↓ (step 1)
Activate venv
  ↓ (step 2)
pip install -r requirements.txt
  ↓ (step 3)
python auto_fix.py (DB consistency check & repair)
  ↓ (step 4)
flask init-db (populate essential data)
  ↓ (step 5)
flask run --host=127.0.0.1 --port=5000 (dev server starts)
```

### Testing & Validation Flow
```
pytest test_app.py (quick test)
  ↓
python run_all_tests.py (full test suite)
  ↓
python diagnostico.py (system health)
  ↓
python check_db.py (DB integrity)
```

### Pre-Deployment Flow
```
python check_db.py (verify DB ok)
  ↓
python backup_db.py (safety first!)
  ↓
python run_all_tests.py (must pass)
  ↓
python otimizar_imagens.py (optimize media)
  ↓
python deploy_production_complete.py OR gcloud app deploy
  ↓
python validar_deploy.py (verify deployment)
```

### Maintenance/Recovery Flow
```
python check_db.py (assess situation)
  ↓
python backup_db.py (backup current state)
  ↓
python diagnostico.py (full diagnostics)
  ↓
IF migrations broken:
  └─ python repair_alembic.py
  └─ .\run.ps1
IF venv corrupted:
  └─ python limpeza_total_venv.py
  └─ .\run.ps1
IF DB corrupted:
  └─ python backup_db.py --remove-migrations
  └─ .\run.ps1 clean
  └─ .\run.ps1
```

---

## 📋 Quick Reference Table

| Script | Category | Purpose | Time | When |
|--------|----------|---------|------|------|
| run.ps1 | Core | Start dev | 2-5m | Always first |
| auto_fix.py | Database | DB consistency | Auto | Every startup |
| check_db.py | Diagnostic | DB health | 10s | Troubleshooting |
| backup_db.py | Maintenance | DB backup | 30s | Before changes |
| repair_alembic.py | Recovery | Fix migrations | 1m | After corruption |
| create_admin.py | Setup | Create admin user | 1m | After DB reset |
| test_app.py | Testing | Core tests | 30s | Before commit |
| run_all_tests.py | Testing | Full test suite | 15-20s | Before deploy |
| validar_deploy.py | Validation | Deployment check | 2-3m | After deploy |
| deploy_production_complete.py | Deployment | Full deploy | 5-10m | Release |
| deploy_pythonanywhere_auto.py | Deployment | PythonAnywhere | 3-5m | PythonAnywhere host |
| otimizar_imagens.py | Optimization | Image WebP | 5-30m | Pre-deployment |
| diagnostico.py | Diagnostic | System health | 1-2m | General troubleshooting |
| diagnostico_video_completo.py | Testing | Video check | 1m | Media issues |
| verificar_versao_github.py | Git | Git status | 10s | Before commit |
| limpar_projeto.py | Cleanup | Remove temp files | 30s | Pre-commit |
| limpeza_total_venv.py | Recovery | Venv reset | 5-10m | Emergency |

---

## 🎯 AI Decision Tree for Common Issues

### "The app won't start"
```
1. Run: python check_db.py
   ├─ If DB error → Run: python auto_fix.py
   ├─ If venv error → Run: python limpeza_total_venv.py → .\run.ps1
   ├─ If migrations error → Run: python repair_alembic.py → .\run.ps1
   └─ If import error → Check imports in main code

2. If still failing, run: python diagnostico.py
   └─ Read output for specific issue
```

### "I need to deploy NOW"
```
1. python backup_db.py (safety)
2. python run_all_tests.py (must pass)
3. python otimizar_imagens.py (optimize)
4. python deploy_production_complete.py OR gcloud app deploy
5. python validar_deploy.py (verify)
```

### "Database seems corrupted"
```
1. python backup_db.py (FIRST—ALWAYS!)
2. python check_db.py (diagnose)
3. python repair_alembic.py (fix)
4. python auto_fix.py (additional repair)
5. .\run.ps1 (restart)
6. python check_db.py (verify fixed)
```

### "I want a completely fresh start"
```
1. python backup_db.py --remove-migrations
2. python limpeza_total_venv.py
3. .\run.ps1 clean
4. .\run.ps1
5. python diagnostico.py (verify ok)
```

### "Tests are failing"
```
1. python check_db.py (ensure DB ok)
2. pytest test_app.py -v (see which test fails)
3. Read error output carefully
4. Fix code or run python auto_fix.py
5. pytest test_app.py::failing_test -v (retry specific test)
6. python run_all_tests.py (full suite)
```

---

## 📌 CRITICAL REMINDERS FOR ALL AI AGENTS

### ✅ ALWAYS DO:
1. **Use `run.ps1`** for local development—NEVER `flask run` directly
2. **Backup FIRST** before any destructive operation
3. **Check database** after major operations with `check_db.py`
4. **Run tests** before deployment with `run_all_tests.py`
5. **Validate deployment** with `validar_deploy.py`
6. **Check logs** in `run_log.txt` when operations fail
7. **Filter ConteudoGeral** by BOTH `pagina` AND `secao`
8. **Use migrations** for ALL schema changes—never raw SQL

### ❌ NEVER DO:
1. **Don't bypass `run.ps1`**—it handles critical setup
2. **Don't delete `migrations/`** without backup
3. **Don't hardcode values** in templates/code
4. **Don't upload images** without optimization
5. **Don't disable CSRF** except in test fixtures
6. **Don't query ConteudoGeral** by `secao` alone
7. **Don't commit without** running `run_all_tests.py`
8. **Don't deploy without** running `validar_deploy.py`

### 🔍 Standard Troubleshooting Flowchart
```
Issue Detected?
    ↓
Step 1: Run `python diagnostico.py`
    ↓
Step 2: Run `python check_db.py`
    ├─ DB Error? → `auto_fix.py` → `run_all_tests.py`
    ├─ Import Error? → `limpeza_total_venv.py` → `.\run.ps1`
    ├─ Migration Error? → `repair_alembic.py` → `.\run.ps1`
    └─ Route/Template Error? → Check `run_log.txt`
    ↓
If Resolved: ✓ Continue working
If Not: Review diagnostic output, debug specifically, escalate for help
```

---

This comprehensive guide covers ALL Python scripts in the project ecosystem, their relationships, execution order, and how they work together to maintain the BMA_VF law firm website application.

**For AI Agents**: Use the decision trees above to quickly resolve issues. Always prioritize backup → diagnosis → repair → validation.

**For Humans**: Use the quick reference table to find scripts by purpose, and the flowcharts for standard troubleshooting procedures.

**For CI/CD**: The master test runner and deployment validators provide automated quality gates for your pipelines.

---

## Final Notes for AI Agents

This document provides comprehensive guidance for autonomous AI coding agents working on the BMA_VF project. Key principles:

1. **Database-First Approach**: Always prefer storing configuration and content in `ConteudoGeral` table rather than hardcoding
2. **Migration Discipline**: Never bypass Flask-Migrate; all schema changes go through `flask db migrate` + `flask db upgrade`
3. **CSRF Protection**: Every admin form must include `{{ form.hidden_tag() }}`
4. **Image Optimization**: Use `process_and_save_image()` for all file uploads, never raw saves
5. **Content Separation**: Keep `Pagina` (structure) separate from `ConteudoGeral` (content)
6. **Blueprint Organization**: Respect the three-blueprint pattern (main/auth/admin)
7. **Testing First**: Run tests before commits: `pytest test_app.py` or `python run_all_tests.py`
8. **Deployment Validation**: Always run `python validar_deploy.py` after deployment

### Success Criteria for AI Agents
- ✅ Code follows existing patterns exactly
- ✅ Database migrations created for schema changes
- ✅ All tests pass (`pytest` or `python run_all_tests.py`)
- ✅ No hardcoded values; use `ConteudoGeral` table
- ✅ CSRF tokens present in all admin forms
- ✅ Images processed through `image_processor.py`
- ✅ Comments explain non-obvious logic
- ✅ Git commits have clear, descriptive messages

---

---

## **Per-Script Detailed Reference**

This section contains an expanded, actionable reference for each Python script in the repository. For each script you will find:
- **Purpose**: Why it exists
- **How it works**: High-level steps the script performs
- **Parameters / CLI**: Supported command-line args and environment variables
- **Outputs**: Files, DB changes, log messages, exit codes
- **Example prints / logs**: Suggested messages to add for better traceability
- **Automation patterns**: How to call the script safely in chains (start → test → deploy)
- **Safety notes**: Which operations are destructive and what to backup first

Note: the examples below include recommended `print()` or `logging` messages you can add to the scripts to make runtime flows and failures easier to audit.

---

### `auto_fix.py` (critical)
- Purpose: Ensure DB & migrations consistency at startup; run backups and repair Alembic issues.
- How it works (high-level):
  1. Setup logging to `run_log.txt` and console
  2. Validate `instance/` and migrations folders
  3. If DB present, create timestamped backup to `instance/backups/`
  4. Check Alembic `alembic_version` and migration state; attempt automated repairs
  5. If severe issues detected, exit non-zero after logging remediation steps
- Parameters / CLI:
  - `--dry-run`: validate and report but do not modify files (recommended for CI)
  - `--no-backup`: skip DB backup (dangerous; use only in dev)
  - `--verbose`: more console output
- Outputs:
  - `instance/backups/site.db.YYYYMMDD_HHMMSS` (when backup runs)
  - `run_log.txt` appended with timestamped operations
  - Exit codes: `0` on success, `1` on recoverable errors (with suggested fixes), `2` on unrecoverable errors
- Example prints / logs (recommended):
  - INFO: "auto_fix: starting maintenance run"
  - INFO: "auto_fix: found database at {DB_PATH}, creating backup {backup_path}"
  - WARN: "auto_fix: migrations folder missing — creating baseline"
  - ERROR: "auto_fix: failed to repair alembic_version — manual intervention required"
  - INFO: "auto_fix: finished (duration: {elapsed}s)"
- Automation patterns:
  - Safe startup chain: `python auto_fix.py --dry-run` → review logs → `python auto_fix.py` → `flask init-db`
  - CI: run `python auto_fix.py --dry-run` on PRs to catch migration issues early
- Safety notes:
  - Always run `backup_db.py` before `--no-backup` operations
  - If `auto_fix.py` exits with code 2, stop and collect `run_log.txt`

---

### `run_all_tests.py` (test orchestrator)
- Purpose: Discover and run the full test suite; produce pass/fail summary and optional HTML report.
- How it works:
  1. Scans repo for `test_*.py` files or uses an internal list
  2. Runs tests (pytest) with a timeout per file
  3. Aggregates results, returns non-zero exit if failures
  4. Optionally generates a coverage or HTML report
- Parameters / CLI:
  - `--fast`: run a subset of critical tests (smoke tests)
  - `--coverage`: collect coverage report
  - `--report=path`: save HTML report
- Outputs:
  - Console logs with pass/fail per file
  - Exit code `0` on success, `1` on failures
  - Optional `report.html`
- Example prints / logs:
  - INFO: "run_all_tests: discovered N test files"
  - INFO: "run_all_tests: running test_app.py (1/12)"
  - ERROR: "run_all_tests: test_admin_routes.py failed — see /tmp/test_admin_routes.log"
  - INFO: "run_all_tests: all tests passed"
- Automation patterns:
  - CI job: run `python run_all_tests.py --coverage --report=artifacts/report.html`
  - Pre-deploy hook: fail deployment if exit code non-zero
- Safety notes:
  - Tests assume `WTF_CSRF_ENABLED=False` in fixtures; do not run tests against production DB

---

### `otimizar_imagens.py` / `image_processor.py`
- Purpose: Convert and optimize images to WebP, resize large images, create backups of originals.
- How it works:
  1. Walk `static/images/uploads/` (or configured folder)
  2. For each image, compute output path, resize if width > max, convert to WebP using PIL at 95% quality
  3. Move original to `instance/backups/images_TIMESTAMP/` if configured
- Parameters / CLI:
  - `--src`: source directory (default `static/images/uploads`)
  - `--backup-dir`: directory for original backups
  - `--quality`: JPEG/WebP quality (default 95)
  - `--max-width`: maximum width to keep (default 2560)
- Outputs:
  - Optimized files `*.webp` in same folder or `--out-dir`
  - Backup folders with originals
  - Console summary with counts and total bytes saved
- Example prints / logs:
  - INFO: "otimizar_imagens: found 124 images, processing..."
  - INFO: "otimizar_imagens: image.jpg -> image.webp (orig: 2.3MB, new: 0.6MB)"
  - WARNING: "otimizar_imagens: skipped image.svg (vector)"
  - INFO: "otimizar_imagens: finished. Total saved: 75MB"
- Automation patterns:
  - Pre-deploy step: `python otimizar_imagens.py --src static/images/uploads --backup-dir instance/backups/images` before `deploy_production_complete.py`
  - Cron job: monthly optimization for `instance/backups/`
- Safety notes:
  - Backup originals before bulk overwrite
  - Exclude `favicon.ico` / `logo.svg` if necessary

---

### `backup_db.py`
- Purpose: Safely copy SQLite DB to a timestamped backup file; optional removal of migrations for a clean reset.
- How it works:
  1. Ensure `instance/` and `instance/backups/` exist
  2. Copy `site.db` to `instance/backups/site.db.YYYYMMDD_HHMMSS`
  3. Optionally remove `migrations/` when `--remove-migrations` provided
- Parameters / CLI:
  - `--remove-migrations` (dangerous): remove `migrations/` after backup
  - `--keep N`: keep only last N backups (cleanup)
- Outputs:
  - Backup file(s)
  - Console messages and exit codes
- Example prints / logs:
  - INFO: "backup_db: backing up site.db -> instance/backups/site.db.20251130_120000"
  - INFO: "backup_db: removed 3 old backups"
  - WARNING: "backup_db: --remove-migrations used — migrations/ will be deleted"
- Automation patterns:
  - Always run before `repair_alembic.py`, `limpeza_total_venv.py`, or destructive deploys
  - Integrate as first step in `deploy_production_complete.py`
- Safety notes:
  - NEVER use `--remove-migrations` unless you plan to recreate migrations

---

### `check_db.py`
- Purpose: Lightweight check that database exists and core tables are accessible.
- How it works:
  1. Attempt to connect to DB configured in app (instance/site.db or ENV override)
  2. List tables and try simple queries (e.g., SELECT 1 from user limit 1)
  3. Return non-zero exit code on failure
- Parameters / CLI:
  - `--db path` optional DB path override
- Outputs:
  - Console pass/fail and human-readable table list
  - Exit codes: 0 success, 1 failure
- Example prints / logs:
  - INFO: "check_db: connected to instance/site.db"
  - ERROR: "check_db: cannot open database at {path}"
- Automation patterns:
  - Early step in CI workflows
  - Use before `flask db upgrade` in automated scripts

---

### `diagnostico.py` / `diagnostico_video_completo.py`
- Purpose: Broad system diagnostics (python version, packages, DB, app load, routes). Video script focuses on media checks.
- How it works: runs a set of probes and prints a human-friendly report.
- Parameters: `--verbose`, `--output=path`
- Outputs: console report, optional JSON or file
- Example prints:
  - INFO: "diagnostico: Python 3.11.4 detected"
- Automation patterns: run in pre-deploy pipeline or nightly cron

---

### `deploy_production_complete.py` / `deploy_pythonanywhere_auto.py`
- Purpose: Automate full deployment workflow to production (GAE or PythonAnywhere)
- How it works (GAE example):
  1. Run `run_all_tests.py`
  2. Run `backup_db.py`
  3. Run `otimizar_imagens.py`
  4. Create migration & `flask db upgrade`
  5. Call `gcloud app deploy` or remote deploy
  6. Run `validar_deploy.py`
- Parameters / CLI:
  - `--dry-run`, `--target=pythonanywhere|gae`, `--version=1`
- Outputs: deployment logs, exit codes, validation report
- Example prints:
  - INFO: "deploy_production_complete: starting deployment to GAE"
  - ERROR: "deploy_production_complete: failed at migrations step"
- Automation patterns: run from CI/CD server with secrets provided via env vars
- Safety notes: Always run backups and tests prior to deploy

---

### `validar_deploy.py`
- Purpose: Post-deploy checks (routes, DB, admin, static, env, error pages).
- How it works: runs HTTP checks and DB queries, returns aggregated status
- Parameters: `--base-url`, `--timeout`
- Outputs: console summary and non-zero exit if issues
- Example prints: "validar_deploy: / returned 200, /admin returned 302"

---

### `create_admin.py`
- Purpose: Interactive admin user creation/reset tool
- Parameters: `--username`, `--email`, `--password` (or prompt)
- Outputs: Adds user to DB and prints confirmation
- Example logs: "create_admin: created admin user 'admin' (id=3)"

---

### `limpeza_total_venv.py` & `limpar_projeto.py`
- Purpose: Cleanup and recovery scripts
- How it works: removes venv, caches, temp files; optionally reinstalls requirements
- Parameters: `--reinstall` (recreate venv), `--yes` (skip prompts)
- Outputs: exit codes and console progress
- Warnings: destructive; backup DB first
- Example prints: "limpeza_total_venv: removed venv/ (size: 120MB)"

---

### `fix_missing_images.py`, `fix_seo_all_themes.py`, `fix_all_contrast_issues.py`, `fix_video_posicionamento_final.py`
- Purpose: Content & accessibility fixes for templates and assets
- How it works: scan templates/static files and apply fixes or print candidate fixes
- Parameters: `--fix` to apply changes, otherwise only report
- Outputs: report file and optional patch files
- Example prints: "fix_missing_images: 12 missing images found" / "fix_seo_all_themes: updated meta for home_option4.html"

---

### `verificar_versao_github.py`, `criar_repo_github.py`, `criar_repo_limpo.py`, `criar_zip_limpo.py`
- Purpose: Git helpers and repo bootstrap / packaging scripts
- How it works: query git status, create `.zip` excluding dev artifacts, initialize/clean repo
- Parameters: `--remote`, `--branch`, `--output`
- Outputs: exit codes and artifact files

---

## Recommended logging snippets (copy into top of scripts)
Add this standardized logger snippet to the top of any script to get consistent structured logs:

```python
import logging
import sys

logger = logging.getLogger("bma_vf")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Example usage:
logger.info("auto_fix: starting maintenance run")
logger.warning("backup_db: --remove-migrations provided — destructive")
logger.error("run_all_tests: test suite failed: %s", failure_summary)
```

Place `logger.info(...)` lines at key steps (start, before/after heavy IO, on exceptions, at end with duration).

---

## Where to Add Prints / Logs in Scripts (suggested insertion points)
- `auto_fix.py`: before backup, after backup, before migration checks, after repair, on exception
- `run_all_tests.py`: on discovery, before each test file run, on failure of each file, at end
- `otimizar_imagens.py`: before processing each file, on skip, after conversion, total summary
- `backup_db.py`: before copy, after copy, if removing migrations, cleanup summary

---

## Concrete Log / Print Snippets and Examples
Below are ready-to-paste code snippets and example messages you can insert into the top and critical points of the scripts. They are safe to add and increase runtime observability for both local runs and CI.

1) Standard logger (put near top of any script):

```python
import logging
import sys

def setup_logger(name="bma_vf", level=logging.INFO):
  logger = logging.getLogger(name)
  if logger.handlers:
    return logger
  handler = logging.StreamHandler(sys.stdout)
  formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  logger.setLevel(level)
  return logger

# Usage
logger = setup_logger()
logger.info("script_name: starting")
```

2) Small helper for progress and safe exit (copy into scripts where long-running operations occur):

```python
import time
def log_progress(logger, step, total=None, msg=None):
  if total:
    logger.info(f"progress: step {step}/{total} - {msg or ''}")
  else:
    logger.info(f"progress: {step} - {msg or ''}")

def safe_exit(logger, code=0, msg=None):
  if msg:
    logger.info(f"exiting: {msg}")
  logger.info(f"exit_code={code}")
  raise SystemExit(code)
```

3) `auto_fix.py` - suggested insertion points and messages:

At start:
```python
logger.info("auto_fix: starting maintenance run")
start_ts = time.time()
```

Before DB backup:
```python
logger.info("auto_fix: detected DB at %s; creating backup", DB_PATH)
```

After backup success:
```python
logger.info("auto_fix: backup created at %s", backup_path)
```

On migration-repair attempt:
```python
logger.info("auto_fix: attempting repair for alembic_version")
```

On unrecoverable error:
```python
logger.error("auto_fix: unrecoverable error: %s", str(exc))
safe_exit(logger, code=2, msg="auto_fix unrecoverable")
```

At end:
```python
elapsed = time.time() - start_ts
logger.info("auto_fix: finished (%.2fs)", elapsed)
```

4) `run_all_tests.py` - suggested messages:

On discovery of test files:
```python
logger.info("run_all_tests: discovered %d test files", len(test_files))
```

Before running each file:
```python
logger.info("run_all_tests: running %s (%d/%d)", filename, idx, total)
```

On failure of a file:
```python
logger.error("run_all_tests: %s failed (returncode=%d). See %s", filename, rc, logfile)
```

Summary at end:
```python
logger.info("run_all_tests: completed. passed=%d failed=%d", passed, failed)
```

5) `otimizar_imagens.py` - suggested messages:

At start:
```python
logger.info("otimizar_imagens: scanning %s for images", src_dir)
```

Before processing each image:
```python
logger.info("otimizar_imagens: processing %s", src_path)
```

On skip:
```python
logger.warning("otimizar_imagens: skipping %s (unsupported or small)", filename)
```

After conversion:
```python
logger.info("otimizar_imagens: %s -> %s (orig=%d bytes new=%d bytes)", src_path, out_path, orig_size, new_size)
```

Final summary:
```python
logger.info("otimizar_imagens: finished. processed=%d skipped=%d saved_bytes=%d", processed, skipped, total_saved)
```

6) `backup_db.py` - suggested messages:

Before copy:
```python
logger.info("backup_db: preparing to backup %s to %s", db_path, backup_path)
```

After copy success:
```python
logger.info("backup_db: backup completed -> %s", backup_path)
```

If `--remove-migrations` used:
```python
logger.warning("backup_db: --remove-migrations used: removing %s (ensure you have backup)", migrations_dir)
```

On completion:
```python
logger.info("backup_db: finished successfully")
```

---

Notes:
- These snippets are intentionally small and unobtrusive; they use `logging` instead of `print()` so CI and log aggregation can capture structured messages.
- If you prefer `print()` (for very early bootstrap scripts where logging may be unavailable), use the same messages with `print()` but ensure they are flushed: `print(..., flush=True)`.

If você concorda, o próximo passo é aplicar patches reais em `auto_fix.py` e `run_all_tests.py` para inserir o `setup_logger()` e os `logger.info(...)` nos pontos críticos. Quer que eu aplique esses patches automaticamente agora ou prefere revisar os snippets antes de aplicar? 

## Automation Examples (small recipes)

1) Safe deploy recipe (PowerShell):
```powershell
python .\backup_db.py
python .\run_all_tests.py --coverage --report=artifacts/report.html
python .\otimizar_imagens.py --src static/images/uploads --backup-dir instance/backups/images
python .\deploy_production_complete.py --target=gae --dry-run
python .\deploy_production_complete.py --target=gae
```

2) CI smoke test (GitHub Actions job):
```yaml
- name: Run smoke tests
  run: |
    python -m pip install -r requirements.txt
    python auto_fix.py --dry-run
    python run_all_tests.py --fast
```

---

## Safety checklist before running destructive scripts
- [ ] Run `python backup_db.py` and verify backup exists
- [ ] Run `python check_db.py` to confirm DB connectivity
- [ ] Run `python run_all_tests.py` and fix failures
- [ ] Review `run_log.txt` for recent `auto_fix.py` operations

---

## Next steps (I can do now if you approve)
1. Apply example logging snippet to `auto_fix.py` and `run_all_tests.py` (small patch)
2. Run `python auto_fix.py --dry-run` locally to capture sample logs (requires local Python)
3. Create a short `scripts/README.md` summarizing how to use these scripts in CI

---

*Last Updated: November 30, 2025*  
*Project: Belarmino Monteiro Advogado (BMA_VF)*  
*Documentation Version: 2.5 - Per-Script Detailed Reference Added*
