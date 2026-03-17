# Arquitectura del MVP — Alke Auction
*Python · Django · PostgreSQL (Supabase)*

---

## 1. Respuestas a las Preguntas Reflexivas

### 1.1 Arquitectura y Modelos de Datos

**¿Cuántos modelos Django necesito y cuáles son sus relaciones?**

```
User (Django)
└── UserProfile (1:1)

User
└── Auction (1:N)

Auction
└── Bid (1:N)

Category
└── Auction (1:N)
```

| Modelo        | Rol                            |
|---------------|-------------------------------|
| `User`        | Usuario autenticado            |
| `UserProfile` | Perfil público del usuario     |
| `Category`    | Clasificación de antigüedades  |
| `Auction`     | Subasta publicada              |
| `Bid`         | Ofertas realizadas             |

---

**¿`UserProfile` extiende `AbstractUser` o usa `OneToOneField`?**

Se usa **`OneToOneField` con `User`**.

- Mantiene compatibilidad con `django.contrib.auth`
- Simplifica autenticación y formularios
- Permite agregar campos sin modificar el modelo base
- Arquitectura más mantenible para un MVP

---

**¿El estado de `Auction` se maneja con `CharField` o `SmallIntegerField`?**

```python
status = models.CharField(choices=AuctionStatus.choices)
```

- Más legible en base de datos y en código
- Facilita debugging
- Rendimiento aceptable para un MVP

---

**¿`closing_date` se guarda en UTC?**

Sí.

```python
# settings.py
USE_TZ = True
TIME_ZONE = "UTC"
```

```django
{# Template — conversión a hora local #}
{{ auction.closing_date|localtime }}
```

- Estándar en aplicaciones web distribuidas
- Evita inconsistencias entre zonas horarias

---

**¿Cómo representar la oferta más alta actual?**

Se **desnormaliza** en `Auction`:

```python
current_price = models.DecimalField(...)
```

- Evita `aggregate()` en cada request
- Mejora performance en listados con muchas subastas
- Reduce carga en la base de datos

> La actualización de `current_price` ocurre al registrar una oferta válida.

---

### 1.2 Lógica de Negocio Crítica

**¿Cómo se implementa el cierre automático?**

**Management Command + Cron** (estrategia elegida para el MVP):

```bash
python manage.py close_auctions
```

- Simplicidad de implementación
- No requiere Celery ni Redis
- Fácil de automatizar con `cron`

---

**¿Qué pasa si dos usuarios ofertan simultáneamente?**

Se utiliza `select_for_update()` dentro de una transacción atómica:

```python
with transaction.atomic():
    auction = Auction.objects.select_for_update().get(pk=pk)
    # validar y guardar oferta
```

Previene **race conditions** en concurrencia alta.

---

**¿Dónde validar la lógica de oferta?**

En **dos niveles** (defensa en profundidad):

1. **Vista** — feedback inmediato al usuario (UX)
2. **Modelo `clean()`** — garantía de integridad de datos

---

**¿El vendedor puede editar la subasta con ofertas activas?**

No. Regla implementada en la vista:

```python
if auction.bids.exists():
    # bloquear edición
```

Evita la manipulación del resultado una vez iniciada la puja.

---

### 1.3 Autenticación y Permisos

**¿Sistema de autenticación?**

```python
django.contrib.auth  # nativo de Django
```

- Seguro y probado en producción
- Suficiente para el alcance del MVP

---

**Protección de vistas:**

```python
# Class-Based Views
class MiVista(LoginRequiredMixin, View): ...

# Function-Based Views
@login_required
def mi_vista(request): ...
```

---

**¿Cómo evitar que el vendedor oferte en su propia subasta?**

```python
if request.user == auction.seller:
    raise ValidationError("No puedes ofertar en tu propia subasta.")
```

---

### 1.4 Frontend y UX

**¿Cómo funciona el contador regresivo?**

Implementado **100% en JavaScript (cliente)**:

```javascript
const diff = new Date(closingDate) - Date.now();
```

- Reduce carga del servidor
- Actualización cada segundo sin requests adicionales

---

**¿Cómo se envían las ofertas?**

```html
<form method="POST" action="{% url 'place_bid' auction.pk %}">
```

- `POST` clásico para el MVP
- Evita la complejidad de AJAX / `fetch()`
- Redirige con `messages.success` al detalle de la subasta

---

**Arquitectura de templates:**

```
base.html
 ├── {% block title %}
 ├── {% block content %}
 └── {% block scripts %}
```

---

**Archivos estáticos:**

```
static/
 ├── css/main.css
 ├── js/main.js
 └── img/
```

---

### 1.5 Base de Datos y Deploy

**Gestión de variables sensibles:**

```bash
# .env  (incluido en .gitignore)
SECRET_KEY=...
DEBUG=True
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
```

```python
# settings.py
from decouple import config
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
```

| Entorno    | `DEBUG` |
|------------|---------|
| Local      | `True`  |
| Producción | `False` |

---

### 1.6 Scope del MVP

**Funcionalidades fuera del MVP** (backlog futuro):

- Pagos online
- Notificaciones por email
- WebSockets / tiempo real
- Chat comprador-vendedor
- Ranking de usuarios
- Sistema antifraude

---

**Categorías** — datos estáticos vía fixtures:

```bash
python manage.py loaddata fixtures/categories.json
```

**Buscador** — filtrado simple con ORM:

```python
Auction.objects.filter(title__icontains=q)
```

---

## 2. Arquitectura del Proyecto Django

```
alke-auction/
│
├── manage.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   └── auctions/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── signals.py
│       ├── views.py
│       ├── urls.py
│       ├── services.py
│       ├── validators.py
│       │
│       ├── migrations/
│       │
│       ├── management/
│       │   └── commands/
│       │       └── close_auctions.py
│       │
│       ├── templates/
│       │   └── auctions/
│       │       ├── base.html
│       │       ├── home.html
│       │       ├── auction_detail.html
│       │       ├── auction_create.html
│       │       ├── profile.html
│       │       └── dashboard.html
│       │
│       └── static/
│           └── auctions/
│               ├── css/
│               │   └── main.css
│               ├── js/
│               │   ├── countdown.js
│               │   ├── animations.js
│               │   └── bid.js
│               └── img/
│
├── templates/
│   └── registration/
│       ├── login.html
│       └── register.html
│
├── static/
├── media/
│
└── fixtures/
    └── categories.json
```

---

## 3. Arquitectura de Base de Datos (Supabase / PostgreSQL)

**Tablas principales:**

```
auth_user
user_profile
category
auction
bid
```

**Relaciones:**

```
User ──1:1──► UserProfile
User ──1:N──► Auction
User ──1:N──► Bid
Category ──1:N──► Auction
Auction ──1:N──► Bid
```

---

## 4. Campos Principales de los Modelos

### `UserProfile`

| Campo              | Tipo                    |
|--------------------|-------------------------|
| `user`             | `OneToOneField(User)`   |
| `avatar`           | `ImageField`            |
| `auctions_created` | `IntegerField`          |
| `auctions_won`     | `IntegerField`          |
| `created_at`       | `DateTimeField`         |

### `Category`

| Campo        | Tipo            |
|--------------|-----------------|
| `name`       | `CharField`     |
| `slug`       | `SlugField`     |
| `icon`       | `CharField`     |
| `created_at` | `DateTimeField` |

### `Auction`

| Campo           | Tipo                    |
|-----------------|-------------------------|
| `title`         | `CharField`             |
| `description`   | `TextField`             |
| `image`         | `ImageField`            |
| `base_price`    | `DecimalField`          |
| `current_price` | `DecimalField`          |
| `closing_date`  | `DateTimeField`         |
| `status`        | `CharField` (choices)   |
| `seller`        | `ForeignKey(User)`      |
| `category`      | `ForeignKey(Category)`  |
| `created_at`    | `DateTimeField`         |

### `Bid`

| Campo        | Tipo                    |
|--------------|-------------------------|
| `auction`    | `ForeignKey(Auction)`   |
| `bidder`     | `ForeignKey(User)`      |
| `amount`     | `DecimalField`          |
| `created_at` | `DateTimeField`         |

---

## 5. Comando de Cierre Automático

**Archivo:** `apps/auctions/management/commands/close_auctions.py`

**Proceso de ejecución:**

1. Buscar subastas con `status='active'` y `closing_date <= now()`
2. Verificar existencia de ofertas (`Bid.objects.filter(auction=auction).exists()`)
3. Determinar ganador (oferta con `amount` máximo)
4. Actualizar `status` según resultado

**Estados posibles:**

| Estado      | Condición                        |
|-------------|----------------------------------|
| `active`    | Subasta en curso                 |
| `closed`    | Cerrada con al menos una oferta  |
| `deserted`  | Cerrada sin ninguna oferta       |

---

## 6. Decisiones Arquitectónicas Clave

| Decisión                         | Elección                     | Motivo                           |
|----------------------------------|------------------------------|----------------------------------|
| Perfil de usuario                | `OneToOneField`              | Compatibilidad con `auth`        |
| Estado de subasta                | `CharField` con `choices`    | Legibilidad y debugging          |
| Oferta más alta                  | `current_price` en `Auction` | Performance en listados          |
| Cierre automático                | Management command + cron    | Simplicidad MVP, sin Celery      |
| Contador regresivo               | JavaScript (cliente)         | Sin carga adicional al servidor  |
| Envío de ofertas                 | `POST` clásico               | Menor complejidad                |
| Categorías                       | `fixtures/categories.json`   | Catálogo estático                |
| Variables de entorno             | `python-decouple` + `.env`   | Seguridad y portabilidad         |
| Protección ante concurrencia     | `select_for_update()`        | Evita race conditions            |
| Validación de reglas de negocio  | Vista + `clean()` del modelo | Defensa en profundidad           |
