# MartilloVirtualDjango — Planificación MVP
## Preguntas Reflexivas · Backlog Scrumban · Estrategia de Branches

---

## 🧠 SECCIÓN 1 — Preguntas Reflexivas Antes de Escribir Código

> Responder estas preguntas antes de abrir el editor es la diferencia entre un MVP entregable y un proyecto que se reinicia tres veces.

### 1.1 Arquitectura y Modelos de Datos

- [ ] ¿Cuántos modelos Django necesito y cuáles son sus relaciones exactas? (`User` → `Auction` → `Bid`)
- [ ] ¿`UserProfile` extiende `AbstractUser` o usa un `OneToOneField` con el `User` nativo de Django? ¿Por qué?
- [ ] ¿El modelo `Auction` maneja el estado (`active`, `closed`, `deserted`) con `CharField choices` o con un `SmallIntegerField`? ¿Cuál es más mantenible?
- [ ] ¿El campo `closing_date` de `Auction` se guarda en UTC y se convierte a hora local en el template, o se gestiona desde el backend?
- [ ] ¿Cómo se representa la "oferta más alta actual"? ¿Se calcula con `Bid.objects.filter(...).aggregate(Max('amount'))` en cada request, o se desnormaliza en `Auction.current_price`?

### 1.2 Lógica de Negocio Crítica

- [ ] ¿Cómo se implementa el cierre automático de subastas? ¿Con un **management command** ejecutado por `cron`, con **Celery + Redis**, o con validación lazy en cada request? ¿Cuál es viable para el MVP?
- [ ] ¿Qué pasa si dos usuarios ofertan al mismo precio en el mismo milisegundo? ¿Se usa `select_for_update()` para evitar race conditions?
- [ ] ¿La validación "oferta mayor que la más alta actual" ocurre solo en la vista o también a nivel de modelo con `clean()`?
- [ ] ¿El vendedor puede editar o eliminar su subasta una vez que tiene ofertas? ¿Qué dice la lógica de negocio implícita?

### 1.3 Autenticación y Permisos

- [ ] ¿Uso el sistema de autenticación nativo de Django (`django.contrib.auth`) o implemento JWT? ¿Qué corresponde a un MVP?
- [ ] ¿Cómo protejo las vistas de ofertas para que solo usuarios autenticados accedan? ¿`@login_required` en vistas basadas en función o `LoginRequiredMixin` en CBVs?
- [ ] ¿Cómo verifico en la vista de ofertas que el usuario no es el dueño de la subasta sin exponer lógica en el template?

### 1.4 Frontend y UX

- [ ] ¿El contador regresivo se actualiza desde el servidor (polling) o es puramente JavaScript del lado cliente calculando contra `closing_date`?
- [ ] ¿Las ofertas se envían con un `<form>` clásico (POST + redirect) o con `fetch()` / AJAX para actualización sin recarga?
- [ ] ¿Los templates heredan de un único `base.html` con los bloques `{% block title %}`, `{% block content %}`, `{% block scripts %}`?
- [ ] ¿Cómo se carga `{% load static %}` y dónde vive `static/css/main.css`?

### 1.5 Base de Datos y Deploy

- [ ] ¿Las variables de conexión a Supabase (host, user, password, dbname) se gestionan con `python-decouple` o `django-environ` desde un archivo `.env`? ¿El `.env` está en `.gitignore`?
- [ ] ¿`DEBUG=True` solo en desarrollo local? ¿`ALLOWED_HOSTS` está correctamente configurado para el entorno de entrega?
- [ ] ¿Se crea un `superuser` de Django para poder acceder al admin y cargar categorías iniciales con `loaddata`?

### 1.6 Scope del MVP

- [ ] ¿Qué funcionalidades quedan **fuera** del MVP para no sobre-entregar y atrasar la entrega? (ej: notificaciones por email, sistema de pagos, chat en vivo)
- [ ] ¿Las categorías son datos fijos (`fixtures`) o el admin puede gestionarlas dinámicamente?
- [ ] ¿El buscador por título (HU-08) usa `icontains` en queryset o una librería de full-text search? ¿Cuál es proporcional al MVP?

---

## 📋 SECCIÓN 2 — Backlog de Issues para GitHub Projects (Scrumban)

> **Convención de etiquetas:** `epic`, `task`, `bug`, `frontend`, `backend`, `database`, `devops`, `ux`, `priority:high`, `priority:medium`, `priority:low`

---

### EPIC-01 · Configuración del Proyecto y Entorno

**Descripción:** Setup inicial del repositorio, entorno virtual, Django, PostgreSQL (Supabase) y estructura de directorios.
**Etiquetas:** `epic` `devops` `priority:high`

---

#### TASK-01 · Inicializar repositorio Git y estructura del proyecto

- **Etiquetas:** `task` `devops` `priority:high`
- **Descripción:** Crear repositorio en GitHub, inicializar proyecto Django, configurar `.gitignore` (incluir `.env`, `__pycache__`, `*.pyc`, `db.sqlite3`), crear `README.md` con instrucciones de setup.
- **Criterios de aceptación:**
  - [ ] Repositorio público/privado creado en GitHub con nombre `martillo-virtual-django`
  - [ ] `django-admin startproject config .` ejecutado correctamente
  - [ ] `.gitignore` excluye archivos sensibles y de entorno
  - [ ] `README.md` documenta cómo clonar y ejecutar localmente
  - [ ] Primer commit con mensaje `chore: initial project setup`

---

#### TASK-02 · Configurar entorno virtual e instalar dependencias

- **Etiquetas:** `task` `devops` `priority:high`
- **Descripción:** Crear `venv`, instalar paquetes necesarios y generar `requirements.txt`.
- **Criterios de aceptación:**
  - [ ] `requirements.txt` incluye: `django`, `psycopg2-binary`, `pillow`, `python-decouple`, `whitenoise`
  - [ ] Entorno virtual documentado en `README.md`
  - [ ] `pip freeze > requirements.txt` ejecutado y commiteado

---

#### TASK-03 · Conectar Django con PostgreSQL (Supabase)

- **Etiquetas:** `task` `devops` `database` `priority:high`
- **Descripción:** Configurar `settings.py` para usar Supabase con variables de entorno via `python-decouple`.
- **Criterios de aceptación:**
  - [ ] Archivo `.env` con `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `SECRET_KEY`, `DEBUG`
  - [ ] `settings.py` usa `config()` de `decouple` para todas las variables sensibles
  - [ ] `python manage.py migrate` ejecuta sin errores contra Supabase
  - [ ] `.env` está en `.gitignore`; se provee `.env.example` en el repo

---

#### TASK-04 · Crear aplicación principal `auctions`

- **Etiquetas:** `task` `backend` `priority:high`
- **Descripción:** Ejecutar `python manage.py startapp auctions` y registrar en `INSTALLED_APPS`.
- **Criterios de aceptación:**
  - [ ] App `auctions` creada y registrada en `settings.py`
  - [ ] Estructura de directorios: `templates/auctions/`, `static/auctions/css/`, `static/auctions/js/`, `static/auctions/img/`
  - [ ] `urls.py` de la app creado y enlazado desde `config/urls.py` con `include()`

---

### EPIC-02 · Modelos de Datos (HU-01, HU-02, HU-03, HU-06)

**Descripción:** Definir y migrar todos los modelos Django que representan el dominio del negocio.
**Etiquetas:** `epic` `backend` `database` `priority:high`

---

#### TASK-05 · Modelo `UserProfile`

- **Etiquetas:** `task` `backend` `database` `priority:high`
- **Descripción:** Extender el `User` nativo de Django con un perfil público mediante `OneToOneField`.
- **Criterios de aceptación:**
  - [ ] `UserProfile` tiene: `user (OneToOneField)`, `auctions_won (int, default=0)`, `auctions_created (int, default=0)`, `avatar (ImageField, nullable)`
  - [ ] Signal `post_save` en `User` crea automáticamente un `UserProfile`
  - [ ] Migración generada y aplicada sin errores

---

#### TASK-06 · Modelo `Category`

- **Etiquetas:** `task` `backend` `database` `priority:high`
- **Descripción:** Modelo de categorías predefinidas con fixture inicial.
- **Criterios de aceptación:**
  - [ ] `Category` tiene: `name (CharField unique)`, `slug (SlugField unique)`, `icon (CharField, emoji o clase CSS)`
  - [ ] Fixture `categories.json` con las 9 categorías del brief cargable con `loaddata`
  - [ ] Migración aplicada y `loaddata` documentado en `README.md`

---

#### TASK-07 · Modelo `Auction`

- **Etiquetas:** `task` `backend` `database` `priority:high`
- **Descripción:** Modelo central de la plataforma.
- **Criterios de aceptación:**
  - [ ] Campos: `title`, `description`, `image`, `base_price (DecimalField)`, `closing_date (DateTimeField)`, `status (CharField, choices: active/closed/deserted)`, `seller (FK User)`, `category (FK Category)`, `created_at`
  - [ ] `clean()` valida que `closing_date > timezone.now()`
  - [ ] `__str__` retorna el título
  - [ ] Índice en `closing_date` y `status` para queries frecuentes
  - [ ] Migración aplicada sin errores

---

#### TASK-08 · Modelo `Bid`

- **Etiquetas:** `task` `backend` `database` `priority:high`
- **Descripción:** Modelo de ofertas con validaciones de integridad.
- **Criterios de aceptación:**
  - [ ] Campos: `auction (FK Auction)`, `bidder (FK User)`, `amount (DecimalField)`, `created_at (DateTimeField, auto_now_add)`
  - [ ] `clean()` valida: subasta activa, ofertante ≠ vendedor, monto > oferta más alta actual (o ≥ precio base si no hay ofertas)
  - [ ] `Meta.ordering = ['-created_at']`
  - [ ] Migración aplicada sin errores

---

### EPIC-03 · Autenticación y Perfiles (HU-01)

**Descripción:** Registro, login, logout y perfil público de usuarios.
**Etiquetas:** `epic` `backend` `frontend` `priority:high`

---

#### TASK-09 · Registro de nuevos usuarios

- **Etiquetas:** `task` `backend` `frontend` `priority:high`
- **Descripción:** Vista y formulario de registro con validaciones.
- **Criterios de aceptación:**
  - [ ] `UserCreationForm` extendido con campo `email` obligatorio y único
  - [ ] Vista redirige al home tras registro exitoso con mensaje `messages.success`
  - [ ] Errores de validación (usuario duplicado, email inválido) se muestran en el template
  - [ ] `UserProfile` se crea automáticamente via signal

---

#### TASK-10 · Login y Logout

- **Etiquetas:** `task` `backend` `frontend` `priority:high`
- **Descripción:** Vistas de autenticación usando las vistas nativas de Django.
- **Criterios de aceptación:**
  - [ ] `LoginView` y `LogoutView` de `django.contrib.auth.views` configuradas
  - [ ] `LOGIN_REDIRECT_URL` y `LOGOUT_REDIRECT_URL` definidos en `settings.py`
  - [ ] Navbar muestra "Iniciar Sesión / Registrarse" para anónimos y "Mi Perfil / Cerrar Sesión" para autenticados

---

#### TASK-11 · Perfil público del usuario

- **Etiquetas:** `task` `backend` `frontend` `priority:medium`
- **Descripción:** Página pública con estadísticas y actividad del usuario.
- **Criterios de aceptación:**
  - [ ] Muestra: subastas creadas, subastas ganadas, subastas en las que ofertó
  - [ ] URL: `/perfil/<username>/`
  - [ ] Accesible sin autenticación (perfil público)

---

### EPIC-04 · Gestión de Subastas (HU-02, HU-04, HU-07)

**Descripción:** CRUD de subastas, cierre automático y panel del vendedor.
**Etiquetas:** `epic` `backend` `frontend` `priority:high`

---

#### TASK-12 · Crear subasta (HU-02)

- **Etiquetas:** `task` `backend` `frontend` `priority:high`
- **Descripción:** Formulario para que el vendedor publique una pieza.
- **Criterios de aceptación:**
  - [ ] `AuctionForm` con todos los campos requeridos del brief
  - [ ] Validación: `closing_date` no puede ser en el pasado (error de formulario, no excepción)
  - [ ] Upload de imagen guardada en `MEDIA_ROOT`
  - [ ] Subasta creada con `status='active'` automáticamente
  - [ ] Solo usuarios autenticados acceden (`LoginRequiredMixin`)
  - [ ] Redirect a detalle de la subasta tras crear

---

#### TASK-13 · Detalle de subasta

- **Etiquetas:** `task` `backend` `frontend` `priority:high`
- **Descripción:** Página pública con todos los datos de la subasta e historial de ofertas.
- **Criterios de aceptación:**
  - [ ] Muestra: imagen, título, descripción, precio base, oferta más alta, vendedor, categoría, tiempo restante
  - [ ] Historial de ofertas ordenado de más reciente a más antigua
  - [ ] Formulario de oferta visible solo para usuarios autenticados que no sean el vendedor
  - [ ] URL: `/subastas/<pk>/`

---

#### TASK-14 · Listado y filtrado de subastas (HU-06, HU-08)

- **Etiquetas:** `task` `backend` `frontend` `priority:high`
- **Descripción:** Página principal con filtros por categoría y buscador.
- **Criterios de aceptación:**
  - [ ] Query parameter `?categoria=<slug>` filtra por categoría
  - [ ] Query parameter `?q=<texto>` filtra por título con `icontains`
  - [ ] Ambos filtros son combinables
  - [ ] Paginación de 12 ítems por página

---

#### TASK-15 · Cierre automático de subastas (HU-04)

- **Etiquetas:** `task` `backend` `priority:high`
- **Descripción:** Management command para cerrar subastas expiradas.
- **Criterios de aceptación:**
  - [ ] `python manage.py close_auctions` cierra todas las subastas con `closing_date <= now()` y `status='active'`
  - [ ] Si `Bid.objects.filter(auction=auction).exists()`: `status='closed'`, se identifica al ganador (oferta más alta)
  - [ ] Si no hay ofertas: `status='deserted'`
  - [ ] Comando idempotente (ejecutable múltiples veces sin efectos colaterales)
  - [ ] Documentado en `README.md` cómo programarlo con `cron`

---

#### TASK-16 · Panel del vendedor (HU-07)

- **Etiquetas:** `task` `backend` `frontend` `priority:medium`
- **Descripción:** Dashboard privado con estadísticas del vendedor.
- **Criterios de aceptación:**
  - [ ] Tabla de subastas activas con oferta más alta actual
  - [ ] Tabla de subastas cerradas con precio final y ganador
  - [ ] Estadísticas: total creadas, % de subastas exitosas (con ≥ 1 oferta)
  - [ ] Solo accesible para el propio vendedor (`LoginRequiredMixin`)

---

### EPIC-05 · Sistema de Ofertas (HU-03, HU-05)

**Descripción:** Lógica de pujas con validaciones de negocio y protección ante concurrencia.
**Etiquetas:** `epic` `backend` `priority:high`

---

#### TASK-17 · Vista para realizar una oferta

- **Etiquetas:** `task` `backend` `priority:high`
- **Descripción:** Endpoint POST que procesa una oferta con todas las validaciones.
- **Criterios de aceptación:**
  - [ ] Requiere autenticación (`@login_required`)
  - [ ] Valida: subasta activa, ofertante ≠ vendedor, monto > oferta más alta (o ≥ precio base)
  - [ ] Usa `select_for_update()` para prevenir race conditions
  - [ ] Retorna error con mensaje descriptivo si la validación falla
  - [ ] Redirect a detalle de subasta con `messages.success` si la oferta es aceptada

---

#### TASK-18 · Historial público de ofertas (HU-05)

- **Etiquetas:** `task` `backend` `frontend` `priority:medium`
- **Descripción:** Sección visible en el detalle de la subasta con todas las pujas.
- **Criterios de aceptación:**
  - [ ] Tabla/lista con: avatar o inicial del ofertante, monto, fecha y hora relativa
  - [ ] Ordenada de la más reciente a la más antigua
  - [ ] Visible para cualquier visitante (anónimo o autenticado)

---

### EPIC-06 · Identidad Visual y Frontend (HU-08 + Fase 2 + Fase 3)

**Descripción:** Implementación completa del diseño visual, animaciones y responsividad.
**Etiquetas:** `epic` `frontend` `ux` `priority:high`

---

#### TASK-19 · Sistema de diseño base (variables CSS, tipografía, colores)

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** Configurar la identidad visual del brief en `main.css`.
- **Criterios de aceptación:**
  - [ ] Variables CSS: `--color-ebony: #1A1A2E`, `--color-gold: #C9A84C`, `--color-bone: #F5F0E8`, `--color-burgundy: #6B2D3E`, `--color-ash: #8C8C8C`
  - [ ] Google Fonts `Playfair Display` e `Inter` cargadas en `base.html`
  - [ ] Reset CSS aplicado; `box-sizing: border-box` global
  - [ ] Grid/Flexbox base para layouts responsivos

---

#### TASK-20 · Template base y navbar responsivo

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** `base.html` con navbar, footer y bloques de Django.
- **Criterios de aceptación:**
  - [ ] Navbar con logo, menú de categorías, buscador y botones de auth
  - [ ] Hamburger menu funcional en mobile (≤768px) sin librerías externas
  - [ ] Footer con info del proyecto
  - [ ] Bloque `{% block title %}` y `{% block content %}` definidos

---

#### TASK-21 · Tarjetas de subasta con efectos visuales

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** Componente visual de tarjeta con hover, animación de entrada y contador.
- **Criterios de aceptación:**
  - [ ] Efecto `transform: translateY(-8px)` + `box-shadow` en hover
  - [ ] Animación `fade-in` o `slide-up` al cargar con `IntersectionObserver`
  - [ ] Badge "Cerrando Pronto" en borgoña para subastas con < 2 horas
  - [ ] Imagen con `object-fit: cover` y aspect ratio fijo

---

#### TASK-22 · Contador regresivo animado

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** Contador días/horas/minutos/segundos en cada tarjeta activa.
- **Criterios de aceptación:**
  - [ ] JavaScript puro que calcula `closing_date - Date.now()` cada segundo
  - [ ] `closing_date` pasado al JS via `data-closing="{{ auction.closing_date.isoformat }}"`
  - [ ] Al llegar a cero, muestra "Subasta cerrada" sin recargar
  - [ ] Estilo visual con bloques separados para D/H/M/S

---

#### TASK-23 · Botón de oferta con efecto pulso

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** Botón "Ofertar" con animación CSS `pulse` y confirmación visual al éxito.
- **Criterios de aceptación:**
  - [ ] Animación `@keyframes pulse` con `box-shadow` en dorado
  - [ ] Al aceptarse la oferta: animación de checkmark verde + mensaje de éxito
  - [ ] Botón deshabilitado con estilo visual diferente para subastas cerradas

---

#### TASK-24 · Efectos WOW adicionales (mínimo 2)

- **Etiquetas:** `task` `frontend` `ux` `priority:medium`
- **Descripción:** Efectos visuales creativos más allá de los requisitos del brief.
- **Criterios de aceptación:**
  - [ ] **Efecto 1 sugerido:** Glassmorphism en cards (`backdrop-filter: blur` + `background: rgba`)
  - [ ] **Efecto 2 sugerido:** Partículas o confetti CSS al ganar una subasta
  - [ ] Ambos efectos documentados brevemente en `README.md`
  - [ ] No degradan el performance en mobile (testeado en Chrome DevTools)

---

#### TASK-25 · Responsividad completa

- **Etiquetas:** `task` `frontend` `ux` `priority:high`
- **Descripción:** Verificar y ajustar la experiencia en mobile, tablet y desktop.
- **Criterios de aceptación:**
  - [ ] Breakpoints definidos: `480px`, `768px`, `1024px`, `1280px`
  - [ ] Grid de tarjetas: 1 col (mobile) → 2 col (tablet) → 3-4 col (desktop)
  - [ ] Formularios 100% usables en pantallas de 360px de ancho
  - [ ] Sin scroll horizontal en ningún viewport

---

### EPIC-07 · Calidad, Testing y Entrega

**Descripción:** Verificación de funcionalidades, corrección de bugs y preparación para entrega.
**Etiquetas:** `epic` `devops` `priority:medium`

---

#### TASK-26 · Datos de prueba (fixtures o script)

- **Etiquetas:** `task` `devops` `priority:medium`
- **Descripción:** Poblar la base de datos con datos de demo para la presentación.
- **Criterios de aceptación:**
  - [ ] Script o fixture con: 3 usuarios, 9 categorías, 8+ subastas en distintos estados, 15+ ofertas distribuidas
  - [ ] Documentado en `README.md` con `python manage.py loaddata` o `python seed.py`

---

#### TASK-27 · Configurar Django Admin

- **Etiquetas:** `task` `backend` `priority:low`
- **Descripción:** Registrar modelos en el admin con configuración útil.
- **Criterios de aceptación:**
  - [ ] `Auction`, `Bid`, `Category`, `UserProfile` registrados en `admin.py`
  - [ ] `list_display`, `list_filter` y `search_fields` configurados por modelo
  - [ ] Superuser creado y documentado en `README.md`

---

#### TASK-28 · Revisión final y checklist de entrega

- **Etiquetas:** `task` `devops` `priority:high`
- **Descripción:** Validación completa antes de entregar el proyecto.
- **Criterios de aceptación:**
  - [ ] Todas las HU (HU-01 a HU-08) probadas manualmente
  - [ ] No hay errores `500` ni `TemplateSyntaxError` en ninguna vista
  - [ ] `DEBUG=False` no rompe el sitio (archivos estáticos con `whitenoise`)
  - [ ] `requirements.txt` actualizado
  - [ ] `README.md` completo con instrucciones de instalación y ejecución
  - [ ] Último commit con mensaje `release: MVP v1.0`

---

## 🌿 SECCIÓN 3 — Estrategia de Branches (Git Flow Simplificado)

> Convención de nombres: `tipo/descripcion-corta-en-kebab-case`

### Estructura de Branches

```
main
└── develop
    ├── feature/EPIC-01-project-setup
    ├── feature/EPIC-02-models
    │   ├── feature/TASK-05-user-profile-model
    │   ├── feature/TASK-06-category-model
    │   ├── feature/TASK-07-auction-model
    │   └── feature/TASK-08-bid-model
    ├── feature/EPIC-03-authentication
    │   ├── feature/TASK-09-user-registration
    │   ├── feature/TASK-10-login-logout
    │   └── feature/TASK-11-public-profile
    ├── feature/EPIC-04-auction-management
    │   ├── feature/TASK-12-create-auction
    │   ├── feature/TASK-13-auction-detail
    │   ├── feature/TASK-14-list-filter-auctions
    │   ├── feature/TASK-15-auto-close-auctions
    │   └── feature/TASK-16-seller-dashboard
    ├── feature/EPIC-05-bidding-system
    │   ├── feature/TASK-17-place-bid
    │   └── feature/TASK-18-bid-history
    ├── feature/EPIC-06-frontend-design
    │   ├── feature/TASK-19-css-design-system
    │   ├── feature/TASK-20-base-template-navbar
    │   ├── feature/TASK-21-auction-cards-effects
    │   ├── feature/TASK-22-countdown-timer
    │   ├── feature/TASK-23-bid-button-pulse
    │   ├── feature/TASK-24-wow-effects
    │   └── feature/TASK-25-responsive-layout
    ├── feature/EPIC-07-qa-delivery
    │   ├── feature/TASK-26-seed-data
    │   ├── feature/TASK-27-django-admin
    │   └── feature/TASK-28-final-checklist
    └── hotfix/descripcion-del-bug   ← Solo para bugs críticos en develop
```

### Reglas del Flujo

| Regla | Detalle |
|-------|---------|
| **`main`** | Solo recibe merge de `develop` cuando el MVP está completo y testeado. Protegida contra push directo. |
| **`develop`** | Branch de integración. Siempre debe estar en estado funcional (la app corre sin errores). |
| **`feature/*`** | Una branch por TASK. Se abre desde `develop` y se mergea a `develop` via Pull Request. |
| **`hotfix/*`** | Para bugs bloqueantes descubiertos durante el desarrollo. Se abre desde `develop` y mergea a `develop`. |
| **PRs** | Todo merge a `develop` requiere al menos 1 aprobación (si es trabajo en equipo). |
| **Commits** | Seguir Conventional Commits: `feat:`, `fix:`, `chore:`, `style:`, `refactor:`, `docs:` |

### Ejemplos de Commits Convencionales

```bash
git commit -m "feat(models): add Auction model with status choices and clean() validation"
git commit -m "feat(views): implement place_bid view with select_for_update"
git commit -m "fix(forms): prevent closing_date in the past from passing validation"
git commit -m "style(css): add pulse animation to bid button"
git commit -m "chore(fixtures): add initial categories seed data"
git commit -m "docs(readme): document management command for closing auctions"
git commit -m "refactor(views): extract bid validation logic to model clean()"
```

### Comandos Git de Referencia Rápida

```bash
# Crear branch de feature desde develop
git checkout develop && git pull origin develop
git checkout -b feature/TASK-07-auction-model

# Trabajar, commitear y subir
git add . && git commit -m "feat(models): add Auction model"
git push origin feature/TASK-07-auction-model

# Crear Pull Request en GitHub hacia develop
# (desde la interfaz web o con GitHub CLI: gh pr create --base develop)

# Después del merge, limpiar branch local
git checkout develop && git pull origin develop
git branch -d feature/TASK-07-auction-model
```

---

*Documento generado para: MartilloVirtualDjango MVP · Módulo 7 · Práctica Clase 3*
