# Guía de Harvey en español

Cómo instalar Harvey, ponerlo en marcha y venderle a empresas en México en
español. Los comandos son los mismos en Windows, Mac y Linux, salvo donde se
indica.

> Esta guía no es asesoría legal. Antes de enviar correos en frío, revisa la
> sección "Obligaciones legales" con un abogado.

---

## 1. Lo que necesitas antes de empezar

| Qué | Para qué | Costo aproximado |
|---|---|---|
| Suscripción Claude Pro o Max | Harvey piensa y redacta con ella | la que ya pagas |
| Python 3.11 o más reciente | Correr Harvey | gratis |
| Claude Code (`claude`) | Harvey lo usa por dentro | incluido |
| Un dominio secundario y un buzón de Google Workspace | Enviar los correos | ~12 USD/año el dominio + ~7 USD/mes el buzón |
| Clave de Reoon | Verificar correos antes de enviar | 600 verificaciones gratis al mes |
| Servicio de calentamiento (warmup) | Que tus correos no caigan en spam | desde ~22 USD/mes |

Harvey corre en ciclos cada 15 minutos, así que debe estar en una computadora
que se quede encendida, o en un servidor.

---

## 2. Instalar

### Windows

1. Instala Python desde https://www.python.org/downloads/ (marca "Add Python to PATH").
2. Instala Node.js desde https://nodejs.org y luego, en PowerShell:
   ```powershell
   npm install -g @anthropic-ai/claude-code
   claude login
   ```
3. Descarga Harvey (tu fork o rama) y, dentro de la carpeta:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

### Mac o Linux

```bash
npm install -g @anthropic-ai/claude-code
claude login
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
```

### Servidor Linux con Docker

Inicia sesión en Claude Code en el servidor (`claude login`), copia `.env.example`
a `.env` y luego ejecuta `docker compose up -d`. La configuración y la base de
datos se guardan en la carpeta del proyecto.

Comprueba que Claude responde: `claude -p "di hola"` y luego `harvey status --check`.

> Cada vez que abras una terminal nueva, activa el entorno primero:
> `.venv\Scripts\activate` (Windows) o `source .venv/bin/activate` (Mac/Linux).

---

## 3. El buzón de envío (lo más importante para no caer en spam)

1. **Compra un dominio secundario**, parecido al tuyo pero distinto (por ejemplo
   `tunegocio-mail.com`). **Nunca envíes correos en frío desde tu dominio
   principal**: si se daña su reputación, tus correos normales también caen en spam.
2. Crea un buzón de **Google Workspace** en ese dominio (por ejemplo `nombre@tunegocio-mail.com`).
3. Configura en el DNS del dominio (Google te da los valores en Admin → Gmail → Autenticar correo):
   - **SPF**: registro TXT `v=spf1 include:_spf.google.com ~all`
   - **DKIM**: genera la clave en Google Admin y agrega el registro TXT que te da
   - **DMARC**: registro TXT en `_dmarc` con `v=DMARC1; p=none; rua=mailto:tu-correo`
4. Redirige el dominio secundario a tu sitio principal, para que quien lo visite llegue a tu página.
5. **Calienta el buzón de 2 a 4 semanas** con un servicio de warmup antes de mandar
   cualquier correo en frío. Anota la fecha en que empezaste en `harvey.local.yaml`:
   ```yaml
   channels:
     email:
       warmup:
         start_date: "2026-11-01"
   ```
6. Revisa cómo vas en cualquier momento con `harvey warmup`.

---

## 4. Claves (`.env`)

Copia el archivo de ejemplo y ábrelo con un editor de texto:

```bash
cp .env.example .env        # en Windows: copy .env.example .env
```

**Las claves van solo en `.env`, nunca en un chat ni en GitHub** (el archivo ya está
excluido de git).

- **Gmail**: en https://console.cloud.google.com crea un proyecto, activa la Gmail API,
  y en Credenciales crea un "ID de cliente de OAuth" de tipo "App de escritorio".
  Copia el ID y el secreto en `GMAIL_CLIENT_ID` y `GMAIL_CLIENT_SECRET`. Luego:
  ```bash
  harvey gmail auth     # abre el navegador una sola vez para autorizar
  harvey gmail test     # confirma la conexión
  ```
- **Reoon**: crea una cuenta en https://reoon.com/email-verifier, copia la clave API a
  `REOON_API_KEY`. Sin un verificador, Harvey **no envía nada** (marca los correos como "guess").
- **Opcionales**: `SERPER_API_KEY` (búsquedas de Google, 2,500 gratis) o
  `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` (listados de negocios, muy barato).

---

## 5. Configurar en español

En `harvey.local.yaml` (o `harvey.yaml` si no entrenaste):

```yaml
icp:
  language: "es"        # correos, respuestas y búsquedas en español
  country: "mx"
  geography:
    - "Monterrey, NL"
  geo_coordinates:      # latitud,longitud,radio en km; mejor que solo el nombre
    "Monterrey, NL": "25.6866,-100.3161,30"

channels:
  email:
    provider: "gmail"
    require_approval: true      # nada sale sin que lo apruebes
    link_domains: ["tusitio.com"]   # tu sitio principal

compliance:
  postal_address: "Calle, número, colonia, CP, ciudad, estado"
  opt_out_line: 'Si no te interesa, responde "no gracias" y no vuelvo a escribirte.'

usage:
  quiet_hours:
    timezone: "America/Monterrey"
```

Con `language: "es"`, Harvey:
- redacta y contesta en español de México (de "usted", salvo que el prospecto tutee);
- busca resultados en español en el país indicado;
- reconoce dueños en sitios en español ("Director General", "fundada por…", páginas "Nosotros");
- respeta las bajas en español sin preguntarle al modelo: "no gracias", "dame de baja",
  "no me escriba", "no me interesa", "baja", entre otras;
- pasa a revisión humana cualquier respuesta que mencione un abogado, una demanda o Profeco.

---

## 6. Entrenar, elegir señales y buscar prospectos

```bash
harvey train https://tusitio.com      # aprende qué vendes
harvey signals --confirm free         # activa las señales gratuitas
harvey discover --estimate            # muestra cuánto costaría buscar; no gasta nada
harvey discover                       # fuente gratuita (OpenStreetMap)
harvey discover --provider dataforseo_listings --max-spend 2.00   # fuente de pago, con tope
```

Si tu sitio carga el contenido con JavaScript (como algunos sitios de portales
inmobiliarios), el entrenamiento puede leerlo incompleto. Revisa
`skills/product_knowledge.md` y `harvey.local.yaml`, y corrige a mano lo que falte.

---

## 7. Arrancar y aprobar correos

```bash
harvey dashboard     # abre el panel; usa el enlace privado que imprime
harvey run           # inicia el ciclo (déjalo corriendo en otra terminal)
```

- En el panel, la pestaña **Outbox** muestra cada correo antes de enviarse. Léelo,
  edítalo si hace falta y apruébalo o recházalo. También desde la terminal:
  `harvey outbox`, `harvey outbox --approve <id>`, `harvey outbox --reject <id>`.
- **No envíes el enlace del panel a nadie**: el token que lleva lo desbloquea.
- Para detener todo envío al instante: `harvey sending pause` (y `harvey sending resume`).
- Aprueba a mano al menos uno o dos lotes antes de pensar en el modo automático.

---

## 8. Obligaciones legales

**México**

- **Ley Federal de Protección de Datos Personales en Posesión de los Particulares
  (LFPDPPP, nueva ley de marzo de 2025).** Al tratar nombres y correos de personas
  necesitas un **aviso de privacidad** publicado (en tu sitio) que diga quién eres,
  para qué usas los datos y cómo ejercer los derechos ARCO (acceso, rectificación,
  cancelación y oposición). Si obtienes el dato de una fuente distinta de la persona
  (por ejemplo, su sitio web), debes darle a conocer el aviso en el primer contacto:
  añade al pie una línea corta con la dirección de tu aviso de privacidad.
- **Atiende las bajas de inmediato y para siempre.** Harvey lo hace solo, y además
  puedes poner dominios o correos en `compliance.do_not_contact`.
- **Ley Federal de Protección al Consumidor y Profeco.** La publicidad debe permitir
  dejar de recibirla y respetar a quien lo pida. Si además vas a llamar o mandar
  mensajes, revisa el REPEP de Profeco.
- La autoridad de datos personales cambió en 2025 (el INAI desapareció); confirma con
  tu abogado ante quién se responde hoy.

**Estados Unidos (si contactas empresas allá): CAN-SPAM**

- Dirección postal física en cada correo (`compliance.postal_address`).
- Una forma clara de darse de baja, atendida en máximo 10 días hábiles (Harvey la añade y la respeta).
- Asunto y remitente que no engañen; nada de "Re:" falsos.

**Lo que Harvey no debe hacer**

- La automatización de LinkedIn viola sus términos: déjala apagada (`channels.linkedin.enabled: false`).
- No uses listas compradas: casi siempre rebotan y dañan el dominio.
