# Alke Auction — Contexto del Proyecto para el Agente

## Stack tecnológico
- Python 3.12 + Django 5.x
- PostgreSQL vía Supabase (psycopg2-binary)
- HTML + CSS + JavaScript vanilla (sin frameworks JS)
- python-decouple para variables de entorno
- whitenoise para archivos estáticos en producción
- pillow para manejo de imágenes

## Estructura de carpetas
```
alke_auction/
├── config/          # Configuración Django (settings, urls, wsgi, asgi)
├── apps/
│   └── auctions/    # App principal
│       ├── models.py
│       ├── views.py
│       ├── forms.py
│       ├── urls.py
│       ├── admin.py
│       ├── signals.py
│       ├── services.py
│       ├── validators.py
│       ├── migrations/
│       ├── management/commands/close_auctions.py
│       ├── templates/auctions/
│       └── static/auctions/css|js|img/
├── templates/registration/  # login.html, register.html
├── fixtures/categories.json
├── media/
├── .env             # NO commitear — ver .env.example
└── requirements.txt
```

## Modelos y relaciones
```
User (Django nativo)
 ├── UserProfile     (OneToOneField — creado via signal post_save)
 ├── Auction         (ForeignKey — subastas publicadas como vendedor)
 └── Bid             (ForeignKey — ofertas realizadas como comprador)

Category
 └── Auction         (ForeignKey)

Auction
 └── Bid             (ForeignKey)
```

## Decisiones arquitectónicas — NO cambiar sin consultar
- `UserProfile` usa `OneToOneField(User)`, NO extiende `AbstractUser`
- `Auction.status` es `CharField` con choices: `active`, `closed`, `deserted`
- `Auction.current_price` está desnormalizado (se actualiza al registrar cada oferta)
- `USE_TZ = True` y `TIME_ZONE = "UTC"` en settings — conversión a hora local en templates
- Cierre automático: management command `close_auctions` (sin Celery)
- Envío de ofertas: `POST` clásico con redirect (sin AJAX)
- Contador regresivo: JavaScript cliente puro (sin polling al servidor)
- Categorías: datos estáticos cargados con `loaddata fixtures/categories.json`
- Buscador: `Auction.objects.filter(title__icontains=q)` (sin full-text search)

## Reglas de negocio críticas
- El vendedor NO puede ofertar en su propia subasta
- Toda oferta se procesa dentro de `transaction.atomic()` con `select_for_update()`
- Una oferta debe ser estrictamente mayor que `current_price` (o >= `base_price` si no hay ofertas)
- No se pueden crear subastas con `closing_date` en el pasado (validado en `clean()`)
- Una subasta con ofertas activas NO puede ser editada por el vendedor
- Las ofertas en subastas cerradas son rechazadas

## Validaciones — siempre en dos niveles
1. **Vista**: feedback inmediato al usuario con `messages.error`
2. **Modelo `clean()`**: garantía de integridad de datos

## Convenciones de código
- Vistas: Class-Based Views (CBVs) con `LoginRequiredMixin`
- Decoradores FBV: `@login_required` solo si la vista es simple
- Nombres de templates: `auctions/<modelo>_<accion>.html`
- URLs con nombre: `{% url 'auction_detail' pk=auction.pk %}`
- Variables de entorno: siempre via `config()` de `python-decouple`
- Commits: Conventional Commits — `feat:`, `fix:`, `chore:`, `style:`, `refactor:`, `docs:`

## Variables de entorno requeridas (.env)
```
SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## Identidad visual (Fase 2 del brief)
- Fondo principal: `#1A1A2E` (Negro Ébano)
- Acentos y botones: `#C9A84C` (Dorado Antiguo)
- Texto sobre oscuro: `#F5F0E8` (Blanco Hueso)
- Urgencia / badges: `#6B2D3E` (Borgoña)
- Texto secundario: `#8C8C8C` (Gris Ceniza)
- Títulos: `Playfair Display` (Google Fonts)
- Cuerpo: `Inter` (Google Fonts)

## Efectos visuales obligatorios (Fase 3 del brief)
1. Contador regresivo animado en cada tarjeta (D/H/M/S)
2. Efecto hover en tarjetas: `transform: translateY(-8px)` + box-shadow
3. Animación de entrada con `IntersectionObserver` (fade-in o slide-up)
4. Botón "Ofertar" con animación `@keyframes pulse` en dorado
5. Confirmación visual animada al aceptar oferta (checkmark verde)
6. Diseño 100% responsivo — breakpoints: 480px, 768px, 1024px, 1280px
7. Estética moderna: glassmorphism, gradientes sutiles, micro-animaciones
8. Mínimo 2 efectos WOW adicionales a elección

## Fuera del MVP — NO implementar
- Pagos online
- Notificaciones por email
- WebSockets / tiempo real
- Chat comprador-vendedor
- Ranking de usuarios
- Sistema antifraude
- AJAX / fetch para ofertas
- Celery / Redis

## Comandos útiles de referencia
```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py close_auctions
python manage.py loaddata fixtures/categories.json
python manage.py createsuperuser
python manage.py collectstatic
```
