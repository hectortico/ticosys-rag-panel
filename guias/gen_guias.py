"""
Generador de las 7 guías PDF de TicoSys con el nuevo branding:
- Banda superior azul 4px
- Logo TicoSys
- Footer con firma corta TicoSys
- Numeración de página
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                 Paragraph, Spacer, Table, TableStyle, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

OUT_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(OUT_DIR, 'logo-ticosys.jpg')

# Brand colors
BLUE = HexColor('#0066CC')
DARK = HexColor('#111827')
GRAY_TEXT = HexColor('#374151')
GRAY_SOFT = HexColor('#6b7280')
LINE = HexColor('#e5e7eb')
BG_HEADER = HexColor('#eff6ff')
BG_CALLOUT = HexColor('#fef3c7')
BG_ROW = HexColor('#f8fafc')

# Styles
H1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=20, textColor=BLUE,
                    spaceAfter=10, leading=24)
H2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14, textColor=BLUE,
                    spaceBefore=14, spaceAfter=6, leading=18)
H3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=11, textColor=DARK,
                    spaceBefore=8, spaceAfter=4, leading=14)
BODY = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, textColor=GRAY_TEXT,
                      leading=15, spaceAfter=4)
LISTI = ParagraphStyle('List', parent=BODY, leftIndent=14)
CODE = ParagraphStyle('Code', fontName='Courier', fontSize=9, textColor=DARK,
                      backColor=HexColor('#f3f4f6'), leftIndent=8, rightIndent=8,
                      spaceBefore=4, spaceAfter=4, leading=13)
CALLOUT = ParagraphStyle('Callout', fontName='Helvetica', fontSize=10, textColor=DARK,
                          leading=15)


def header_footer(canvas, doc):
    canvas.saveState()
    W, H = A4
    # Top blue band 4mm
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 4 * mm, W, 4 * mm, fill=1, stroke=0)
    # Logo
    try:
        canvas.drawImage(LOGO_PATH, 15 * mm, H - 32 * mm,
                          width=46 * mm, height=24 * mm,
                          mask='auto', preserveAspectRatio=True)
    except Exception:
        pass
    # Footer divider
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 28 * mm, W - 15 * mm, 28 * mm)
    # Footer signature
    canvas.setFillColor(DARK)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(15 * mm, 23 * mm, 'TicoSys')
    canvas.setFillColor(GRAY_TEXT)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(15 * mm, 19 * mm, 'info@ticosys.com  ·  ticosys.com')
    canvas.setFillColor(DARK)
    canvas.drawString(15 * mm, 14 * mm,
                       'Si quieres automatizar cualquier otro proceso para tu empresa, visita nuestra web:')
    canvas.setFillColor(BLUE)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(15 * mm, 10 * mm, 'https://ticosys.com')
    # Page number
    canvas.setFillColor(GRAY_SOFT)
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(W - 15 * mm, 10 * mm, f'pág. {canvas.getPageNumber()}')
    canvas.restoreState()


def render_blocks(story, blocks, doc_width):
    for kind, data in blocks:
        if kind == 'h2':
            story.append(Paragraph(data, H2))
        elif kind == 'h3':
            story.append(Paragraph(data, H3))
        elif kind == 'p':
            story.append(Paragraph(data, BODY))
        elif kind == 'list':
            for item in data:
                story.append(Paragraph(f'•&nbsp;&nbsp;{item}', LISTI))
        elif kind == 'olist':
            for i, item in enumerate(data, 1):
                story.append(Paragraph(f'<b>{i}.</b>&nbsp;&nbsp;{item}', LISTI))
        elif kind == 'code':
            escaped = data.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
            t = Table([[Paragraph(escaped, CODE)]], colWidths=[doc_width])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f3f4f6')),
                ('LINEBEFORE', (0, 0), (0, -1), 3, HexColor('#9ca3af')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))
        elif kind == 'callout':
            t = Table([[Paragraph(data, CALLOUT)]], colWidths=[doc_width])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_CALLOUT),
                ('LINEBEFORE', (0, 0), (0, -1), 3, HexColor('#f59e0b')),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))
        elif kind == 'table':
            rows = data['rows']
            # Wrap cell contents
            wrapped = []
            for r_idx, row in enumerate(rows):
                wrapped.append([Paragraph(str(c), BODY if r_idx > 0 else H3) for c in row])
            n = len(rows[0])
            col_widths = data.get('col_widths') or [doc_width / n] * n
            t = Table(wrapped, colWidths=col_widths, repeatRows=1)
            ts = [
                ('BACKGROUND', (0, 0), (-1, 0), BG_HEADER),
                ('BOX', (0, 0), (-1, -1), 0.5, LINE),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, LINE),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]
            for i in range(1, len(rows)):
                if i % 2 == 0:
                    ts.append(('BACKGROUND', (0, i), (-1, i), BG_ROW))
            t.setStyle(TableStyle(ts))
            story.append(Spacer(1, 4))
            story.append(t)
            story.append(Spacer(1, 6))
        elif kind == 'spacer':
            story.append(Spacer(1, data))


def make_pdf(filename, title, blocks):
    out_path = os.path.join(OUT_DIR, filename)
    doc = BaseDocTemplate(
        out_path, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=38 * mm, bottomMargin=32 * mm,
        title=title, author='TicoSys',
    )
    frame_h = A4[1] - 38 * mm - 32 * mm
    frame = Frame(15 * mm, 32 * mm, A4[0] - 30 * mm, frame_h, id='content',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=header_footer)])
    story = [Paragraph(title, H1)]
    render_blocks(story, blocks, A4[0] - 30 * mm)
    doc.build(story)
    print(f'  generated: {out_path} ({os.path.getsize(out_path)} bytes)')


# =====================================================================
# GUIA 00 - Bienvenida y Primeros Pasos
# =====================================================================
guia_00 = [
    ('p', '¡Felicidades! Tu asistente de IA ya está activo y listo para responder a tus clientes 24/7. Esta guía te lleva de la mano por los primeros 30 minutos de uso.'),
    ('h2', 'Paso 1 — Entra a tu panel de conversaciones'),
    ('olist', [
        'Abre en tu navegador: <b>https://crm.ticosys.com</b>',
        'Usa el email y contraseña inicial que te enviamos en el correo de bienvenida',
        'Verás tu panel con la bandeja de entrada (Inbox) vacía al principio',
    ]),
    ('h2', 'Paso 2 — Cambia tu contraseña (importante)'),
    ('olist', [
        'Click en tu <b>avatar</b> (esquina superior derecha)',
        '<b>Profile Settings</b> → <b>Change Password</b>',
        'Pon una contraseña nueva, fuerte, que solo tú sepas',
        'Guarda',
    ]),
    ('h2', 'Paso 3 — Familiarízate con el panel'),
    ('p', 'Las secciones principales son:'),
    ('table', {
        'rows': [
            ['Sección', 'Para qué sirve'],
            ['Conversations', 'Todas las conversaciones de tus clientes, en tiempo real'],
            ['Contacts', 'Lista de personas que han escrito al bot'],
            ['Reports', 'Estadísticas de uso, tiempos de respuesta, leads'],
            ['Settings', 'Configuración (no toques nada aquí sin antes consultar con TicoSys)'],
        ],
        'col_widths': [55 * mm, 125 * mm],
    }),
    ('h2', 'Paso 4 — Cómo funcionan las conversaciones'),
    ('p', '<b>El bot responde automáticamente</b> a las preguntas de los visitantes con la información que has cargado.'),
    ('h3', 'Si quieres tomar el control de una conversación'),
    ('list', [
        'Abre la conversación',
        'Click en <b>"Assign agent"</b> → selecciónate a ti mismo',
        '<b>El bot se detiene automáticamente</b> en esa conversación',
        'Tú respondes en directo',
    ]),
    ('h3', 'Para que el bot vuelva a tomarla'),
    ('list', [
        'Desasígnate (Assign agent → ninguno) o asígnaselo a "Asistente IA"',
        'El bot retoma desde donde quedó, manteniendo el contexto de la conversación',
    ]),
    ('callout', 'Si tú escribes información que el bot no tiene en su base de conocimiento (por ejemplo, una promoción que mencionaste de palabra), el bot puede confundirse al retomar. Es comportamiento esperado: el bot solo conoce lo que está en su RAG.'),
    ('h2', 'Paso 5 — Las etiquetas de colores (Labels)'),
    ('p', 'El bot organiza automáticamente las conversaciones con etiquetas:'),
    ('table', {
        'rows': [
            ['Etiqueta', 'Significado'],
            ['nueva-consulta', 'Un nuevo cliente acaba de escribir'],
            ['cita-agendada', 'El bot le agendó una cita'],
            ['seguimiento-enviado', 'Bot envió email de seguimiento'],
            ['cliente-ganado', 'Marca tú cuando un lead se convierte en venta'],
            ['cliente-perdido', 'Marca tú cuando un lead no compra'],
            ['no-contactar', 'El cliente pidió no recibir más mensajes (baja automática)'],
            ['requiere-humano', 'El bot detectó que necesita intervención tuya'],
        ],
        'col_widths': [55 * mm, 125 * mm],
    }),
    ('h2', 'Paso 6 — Qué hace el bot fuera del chat'),
    ('list', [
        '<b>Recordatorios:</b> 1 hora antes de cada cita, el bot envía email recordatorio al cliente',
        '<b>Seguimiento de leads:</b> cada día revisa los leads que quedaron sin agendar y les envía un email amable',
        '<b>Baja automática:</b> si un cliente pulsa "Date de baja" en el email de seguimiento, se etiqueta y no se le vuelve a escribir',
        '<b>Resumen diario:</b> recibes un email cada mañana con la actividad del día (leads nuevos, citas, conversiones)',
    ]),
    ('h2', 'Próximos pasos: configuraciones opcionales'),
    ('p', 'Para que tu bot funcione al 100%, mira las guías adjuntas según lo que quieras activar:'),
    ('list', [
        '<b>Guía 01 — Documentos para el Bot</b> · Sube tus precios, FAQs, manuales',
        '<b>Guía 02 — Conectar WhatsApp Business</b> · Para que el bot atienda WhatsApp',
        '<b>Guía 02b — Conectar Telegram</b> · Para que el bot atienda Telegram (más simple que WhatsApp)',
        '<b>Guía 03 — Compartir Google Calendar</b> · Para que el bot agende citas (con videollamada Google Meet incluida)',
        '<b>Guía 04 — Compartir Google Drive</b> · Para que el bot envíe archivos/imágenes a clientes',
        '<b>Guía 05 — Emails desde tu correo</b> · Para que los emails automáticos del bot salgan desde tu dominio',
    ]),
    ('h2', '¿Dudas? Soporte'),
    ('p', 'Escribe a <b>info@ticosys.com</b> y te ayudamos.'),
]

# =====================================================================
# GUIA 01 - Documentos para el Bot
# =====================================================================
guia_01 = [
    ('p', 'El bot necesita conocer tu negocio para poder responder bien. Esta guía te ayuda a preparar y enviarnos los documentos correctos.'),
    ('h2', '¿Qué documentos enviar?'),
    ('p', 'Lo más importante (en orden de prioridad):'),
    ('table', {
        'rows': [
            ['Documento', 'Por qué es importante', 'Formato'],
            ['Lista de precios / catálogo', 'Para que el bot conteste preguntas sobre coste', 'Excel (.xlsx) o PDF'],
            ['Preguntas frecuentes (FAQ)', 'Para resolver dudas comunes sin tu intervención', 'PDF, Word o texto'],
            ['Servicios / productos detallados', 'Para describir lo que ofreces', 'PDF o Word'],
            ['Información de contacto', 'Horarios, dirección, teléfonos', 'PDF o Word'],
            ['Procedimiento de trabajo', 'Cómo se contrata, plazos, garantías', 'PDF o Word'],
            ['Política de devoluciones / garantías', 'Si aplica', 'PDF o Word'],
        ],
        'col_widths': [60 * mm, 75 * mm, 45 * mm],
    }),
    ('h2', 'Formatos aceptados'),
    ('list', [
        '<b>PDF</b> (mejor opción para manuales)',
        '<b>XLSX / CSV</b> (mejor para listas de precios — el bot lee fila por fila)',
        '<b>TXT</b> (texto plano)',
        '<b>DOCX</b> (Word)',
    ]),
    ('callout', '<b>NO sirven:</b> imágenes con texto (.jpg/.png con tabla escaneada), audios sin transcribir.'),
    ('h2', 'Consejos para que el bot conteste mejor'),
    ('olist', [
        '<b>Sé específico:</b> en vez de "tenemos servicios variados", escribe "ofrecemos 3 tipos de servicios: A, B y C, con precios desde X€"',
        '<b>Estructura por secciones:</b> usa títulos claros (Servicios, Precios, Horarios...)',
        '<b>Evita ambigüedades:</b> "según el caso" → mejor da rangos concretos',
        '<b>Incluye sinónimos:</b> si vendes "infusiones", menciona también "tisanas", "tés", etc.',
        '<b>Actualiza cuando cambien precios:</b> avísanos para reemplazar el documento',
    ]),
    ('h2', 'Ejemplo bueno vs malo'),
    ('h3', 'Mal'),
    ('callout', '<i>"Hacemos tarot. Las consultas tienen un precio razonable. Contáctanos para saber más."</i>'),
    ('h3', 'Bien'),
    ('callout', '<i>"Servicios de tarot:<br/>• Consulta básica: 30 minutos → 35€<br/>• Consulta extendida: 60 minutos → 65€<br/>• Tirada de pareja: 45 minutos → 50€<br/>• Lectura por WhatsApp/Email: 25€<br/><br/>Horarios: lunes a viernes, 10:00–20:00. Sábados 10:00–14:00."</i>'),
    ('h2', '¿Cómo nos los envías?'),
    ('h3', 'Opción A — Google Drive (recomendado)'),
    ('olist', [
        'Crea una carpeta en tu Drive llamada "Documentos Bot — [tu negocio]"',
        'Sube ahí todos los archivos',
        'Compártela con: <b>ticosysinfo@gmail.com</b> con permisos de lectura',
        'Envíanos el link de la carpeta por email',
    ]),
    ('h3', 'Opción B — Por email directo'),
    ('olist', [
        'Adjunta los archivos a un email',
        'Envía a <b>info@ticosys.com</b>',
        'Asunto: "Documentos bot — [nombre de tu empresa]"',
    ]),
    ('h2', '¿Cuándo el bot estará entrenado?'),
    ('list', [
        '<b>Mismo día:</b> cargamos los archivos a la memoria del bot (proceso de "indexado")',
        '<b>24 horas máximo:</b> el bot ya contesta preguntas basadas en tus documentos',
        '<b>Te avisamos por email</b> cuando esté listo',
    ]),
    ('h2', 'Después: ¿puedes añadir más documentos?'),
    ('p', 'Sí, en cualquier momento. Solo envíanos los nuevos a info@ticosys.com y los cargamos. Si compartiste tu carpeta de Drive, también puedes subirlos ahí directamente y avisarnos.'),
    ('p', '¿Dudas? Escribe a <b>info@ticosys.com</b>'),
]

# =====================================================================
# GUIA 02 - WhatsApp Business
# =====================================================================
guia_02 = [
    ('p', 'Esta guía te lleva por el proceso de Meta (Facebook) para que tu bot pueda recibir y responder mensajes de WhatsApp. <b>El proceso completo toma 20-30 minutos en tu lado</b>, y la conexión técnica final la hacemos nosotros en Chatwoot tras recibir tus 4 datos.'),
    ('callout', '<b>¿Te parece muy complicado?</b> Si no necesitas WhatsApp específicamente, <b>Telegram es mucho más rápido</b> (5 minutos, sin Meta, sin verificación). Mira la <b>Guía 02b — Conectar Telegram</b>.'),
    ('h2', 'Antes de empezar — Requisitos'),
    ('list', [
        '<b>Un número de teléfono</b> que NO esté usando WhatsApp normal ni WhatsApp Business app actualmente (puede ser fijo o móvil)',
        'Cuenta de <b>Facebook personal</b> (la tuya normal)',
        '<b>Cuenta Meta Business Manager</b> (si no tienes, se crea durante el proceso)',
        '<b>Tarjeta de crédito</b> (Meta cobra por mensajes salientes después de 1000/mes gratis)',
    ]),
    ('h2', 'PASO 1 — Crear cuenta Meta Business Manager'),
    ('olist', [
        'Ve a <b>https://business.facebook.com</b>',
        'Click en "Crear cuenta"',
        'Rellena: nombre de tu negocio · tu nombre · email de trabajo',
        'Verifica tu email',
        'Listo, tienes acceso a Business Manager',
    ]),
    ('h2', 'PASO 2 — Verificar tu negocio en Meta (importante)'),
    ('p', 'Sin esto, no puedes enviar más de unos pocos mensajes al día.'),
    ('olist', [
        'En Business Manager → <b>Configuración</b> → <b>Información del negocio</b>',
        'Click en "Iniciar verificación"',
        'Tendrás que subir: documento legal del negocio (escritura, alta autónomos, etc.) y factura de servicios (luz, teléfono) a nombre del negocio. O confirmación por llamada/SMS.',
        'Meta tarda <b>2-5 días</b> en aprobar la verificación',
    ]),
    ('callout', 'Mientras tanto puedes continuar los siguientes pasos y empezar a probar con un número de prueba.'),
    ('h2', 'PASO 3 — Crear App de WhatsApp en Meta for Developers'),
    ('olist', [
        'Ve a <b>https://developers.facebook.com/apps</b>',
        'Click en "Crear app"',
        'Selecciona "Empresa" como tipo de app',
        'Nombre de la app: algo como <i>WhatsApp Bot [Tu Negocio]</i>',
        'Email de contacto: tu email',
        'Asocia la app a tu cuenta de Business Manager',
        'Click en "Crear app"',
    ]),
    ('h2', 'PASO 4 — Añadir el producto "WhatsApp" a la app'),
    ('olist', [
        'Dentro de tu app, busca "WhatsApp" en "Añadir productos"',
        'Click "Configurar"',
        'Selecciona la cuenta de Business Manager',
        'Acepta los términos',
        'Te llevará a la sección "API Setup" (guarda esta pantalla)',
    ]),
    ('h2', 'PASO 5 — Obtener los 4 datos que TicoSys necesita'),
    ('h3', '1. Phone Number ID'),
    ('p', 'En "From" o "Información del número". Es un número largo, ej: <font face="Courier">123456789012345</font>'),
    ('h3', '2. WhatsApp Business Account ID (WABA ID)'),
    ('p', 'Misma pantalla, sección "WhatsApp Business Account ID". También número largo.'),
    ('h3', '3. Access Token temporal'),
    ('p', 'Botón "Generate temporary access token" → token largo que empieza por <font face="Courier">EAA...</font> Cópialo, PERO ojo: este expira en 24h. Hay que generar uno permanente (paso 6).'),
    ('h3', '4. Tu número de teléfono'),
    ('p', 'El número con prefijo internacional, ej: <font face="Courier">+34666123456</font>'),
    ('h2', 'PASO 6 — Generar Access Token PERMANENTE'),
    ('olist', [
        'En tu app → "Configuración del negocio" o "Business settings"',
        '"Usuarios" → "Usuarios del sistema"',
        'Click "Añadir" → tipo "Admin"',
        'Nombre: ej <i>Token Bot</i>',
        'Una vez creado, click en ese usuario → "Generate new token"',
        'Selecciona tu app',
        'Marca los permisos: <font face="Courier">whatsapp_business_messaging</font> y <font face="Courier">whatsapp_business_management</font>',
        'Click "Generate token" → se muestra el token UNA SOLA VEZ',
        'Cópialo y guárdalo en sitio seguro — empieza por <font face="Courier">EAA...</font>',
    ]),
    ('h2', 'PASO 7 — Verificar y registrar tu número de teléfono'),
    ('olist', [
        'En API Setup → "Add phone number"',
        'Introduce tu número con prefijo',
        'Verificación por SMS o llamada (te enviará un código)',
        'Una vez verificado, aparece como "Verified"',
    ]),
    ('h2', 'PASO 8 — Enviarnos los 4 datos'),
    ('p', 'Mándanos un email a <b>info@ticosys.com</b> con asunto <b>"Datos WhatsApp — [tu empresa]"</b> incluyendo:'),
    ('code', 'Phone Number ID: 123456789012345\nWABA ID: 987654321098765\nAccess Token: EAAxxxxxxxxxxxxxxxxxxx...\nNúmero: +34666123456'),
    ('callout', '<b>Importante:</b> el Access Token es como una llave maestra. Mándalo por email seguro y avísanos cuando lo envíes para procesarlo y borrar el email después.'),
    ('h2', 'PASO 9 — Nosotros lo conectamos a tu Chatwoot'),
    ('p', 'Al recibir tus 4 datos, nosotros hacemos la integración técnica en tu Chatwoot:'),
    ('list', [
        'Creamos en tu cuenta de Chatwoot un inbox tipo WhatsApp con tus credenciales',
        'Lo cableamos al workflow del bot',
        'Probamos enviando un mensaje de prueba',
        'Te avisamos cuando esté funcionando (24 horas hábiles)',
        'A partir de ese momento, los mensajes de WhatsApp aparecen en tu Chatwoot junto con los demás canales',
    ]),
    ('h2', 'Costos de Meta'),
    ('p', 'Meta NO cobra por recibir mensajes. Cobra por:'),
    ('list', [
        '<b>Conversaciones iniciadas por el negocio:</b> ~$0.06 USD por conversación (varía por país)',
        '<b>Las primeras 1000 conversaciones del mes son GRATIS</b>',
        'Si solo respondes a clientes que te escriben primero, normalmente caes dentro del free tier',
    ]),
    ('p', 'Más info: <font face="Courier">https://developers.facebook.com/docs/whatsapp/pricing</font>'),
    ('h2', 'Errores comunes'),
    ('table', {
        'rows': [
            ['Error', 'Solución'],
            ['"Phone number not registered"', 'Repite el PASO 7, código por SMS'],
            ['"Access token expired"', 'Generaste un token temporal de 24h. Repite el PASO 6 generando uno permanente'],
            ['"Business not verified"', 'Espera la aprobación de Meta (paso 2). Mientras tanto, solo puedes enviar limitado'],
            ['"Quality rating dropped"', 'Tus mensajes están siendo marcados como spam. Revisa el contenido y la frecuencia'],
        ],
        'col_widths': [60 * mm, 120 * mm],
    }),
    ('p', '<b>¿Te atascas en algún paso?</b> Escribe a info@ticosys.com y te guiamos en directo.'),
]

# =====================================================================
# GUIA 02b - TELEGRAM (NUEVA)
# =====================================================================
guia_02b = [
    ('p', '¿Quieres que tu bot también atienda en Telegram? Es <b>el canal más rápido de conectar</b>: 5 minutos, sin Meta, sin tarjeta de crédito, sin verificaciones.'),
    ('callout', '<b>Telegram vs WhatsApp:</b> si tu público está en WhatsApp, mira la Guía 02. Si tienes una comunidad en Telegram o quieres un canal alternativo más simple, esta es tu guía.'),
    ('h2', '¿Qué necesitas?'),
    ('list', [
        'Tener Telegram instalado en tu móvil o PC',
        'Una cuenta de Telegram (la tuya normal sirve)',
        '5 minutos',
    ]),
    ('h2', 'PASO 1 — Crear el bot con @BotFather'),
    ('olist', [
        'Abre Telegram y busca el usuario <b>@BotFather</b> (es el bot oficial de Telegram para crear bots)',
        'Pulsa <b>Iniciar</b> (o /start)',
        'Escribe el comando: <b>/newbot</b>',
        'BotFather te pide un <b>nombre</b> para tu bot. Pon algo como "Asistente [Tu Negocio]". Este nombre aparece como display name.',
        'BotFather te pide un <b>username</b>. Tiene que terminar en <b>"bot"</b>. Ejemplos válidos: <font face="Courier">mi_negocio_bot</font>, <font face="Courier">TarotAnagaBot</font>. Si está libre, el bot queda creado.',
        'BotFather te devuelve un mensaje con un <b>token</b>. Es una cadena tipo: <font face="Courier">7123456789:AAEabc...</font>',
        '<b>Copia ese token</b> — es la llave que TicoSys necesita.',
    ]),
    ('callout', '<b>El token es secreto.</b> No lo publiques. Si crees que se ha filtrado, vuelve a BotFather → /token → revoca y genera uno nuevo.'),
    ('h2', 'PASO 2 — (Opcional) Personalizar la apariencia de tu bot'),
    ('p', 'Desde el mismo chat con BotFather puedes:'),
    ('list', [
        '<b>/setdescription</b> — descripción que aparece al abrir el chat por primera vez',
        '<b>/setabouttext</b> — texto del perfil del bot',
        '<b>/setuserpic</b> — foto de perfil (logo de tu negocio)',
        '<b>/setcommands</b> — comandos sugeridos (ej. /horarios, /precios) — opcional, el bot responde a lenguaje natural igual',
    ]),
    ('p', 'Todo esto es opcional. Si lo saltas, el bot funciona igual.'),
    ('h2', 'PASO 3 — Enviarnos el token'),
    ('p', 'Si todavía no te has dado de alta en TicoSys: <b>incluye el token en el alta</b> (campo "Token Telegram Bot" del formulario en panel.ticosys.com). En cuanto te demos de alta, tu bot queda conectado a Telegram automáticamente — sin nada más que hacer.'),
    ('p', 'Si ya estás dado de alta y quieres añadir Telegram después: mándanos el token por email a <b>info@ticosys.com</b> con asunto <b>"Telegram — [tu empresa]"</b>:'),
    ('code', 'Token Telegram: 7123456789:AAEabc...\nUsername bot: @TuNegocioBot'),
    ('p', 'Lo configuramos en tu Chatwoot en menos de 5 minutos y te avisamos cuando esté listo.'),
    ('h2', 'Cómo prueban tus clientes'),
    ('olist', [
        'Buscan a tu bot en Telegram por el <b>username</b> (ej. @TarotAnagaBot)',
        'Pulsan <b>Iniciar</b>',
        'Le escriben como a cualquier persona — el bot responde con la información de tu negocio',
    ]),
    ('p', 'También puedes publicar el enlace directo: <font face="Courier">https://t.me/TuNegocioBot</font> en tu web, redes sociales, firma de email, etc.'),
    ('h2', 'Costos'),
    ('p', '<b>Telegram es 100% gratis</b>. Sin límites de mensajes, sin tarjeta de crédito, sin facturación. Ni para ti, ni para Meta, ni para nadie.'),
    ('h2', 'Limitaciones a tener en cuenta'),
    ('list', [
        'Telegram en España y Latinoamérica tiene menos penetración que WhatsApp — verifica que tu público lo usa',
        'No hay verificación oficial de empresa como en WhatsApp Business (algunos clientes pueden dudar)',
        'Los archivos hasta <b>50 MB</b> (más permisivo que WhatsApp, que limita a 16 MB)',
    ]),
    ('h2', 'Errores comunes'),
    ('table', {
        'rows': [
            ['Problema', 'Solución'],
            ['"Username already taken"', 'Otro bot ya usa ese username. Prueba otra variación (debe terminar en "bot")'],
            ['"Sorry, this username is reserved"', 'BotFather no acepta ciertos nombres. Cambia.'],
            ['"El bot no responde"', 'Verifica que nos enviaste el token correcto. El token es sensible a mayúsculas/minúsculas.'],
            ['"Quiero revocar el token"', 'Vuelve a BotFather → /token → selecciona tu bot → revoca y genera uno nuevo. Avísanos el nuevo.'],
        ],
        'col_widths': [60 * mm, 120 * mm],
    }),
    ('p', '<b>¿Dudas?</b> Escribe a info@ticosys.com y te ayudamos.'),
]

# =====================================================================
# GUIA 03 - Google Calendar (FIX: ticosysinfo@gmail.com + Meet)
# =====================================================================
guia_03 = [
    ('p', 'Para que tu bot pueda <b>agendar citas</b> automáticamente con tus clientes, necesita acceso a un calendario de Google.'),
    ('p', '<b>Tiempo total:</b> 3 minutos.'),
    ('h2', '¿Qué hará el bot exactamente?'),
    ('list', [
        '<b>Verificar disponibilidad</b> antes de proponer horarios al cliente',
        '<b>Crear eventos</b> en tu calendario cuando agendan una cita',
        '<b>Generar enlace de Google Meet</b> automáticamente con cada cita (videollamada lista, sin que tengas que crearla a mano)',
        '<b>Enviar email de confirmación</b> al cliente con la fecha, hora y enlace de Meet',
        '<b>Enviar recordatorio</b> al cliente 1 hora antes de la cita',
        '<b>Buscar y cancelar</b> citas si el cliente lo pide al bot',
    ]),
    ('callout', '<b>NO hace nada más</b> — no borra eventos existentes que no creó él, no modifica tus eventos personales, no comparte tu agenda con otros.'),
    ('h2', '¿Qué calendario usar?'),
    ('h3', 'Opción A — Tu calendario principal (más simple)'),
    ('p', 'Si todas las citas que agenda el bot van a tu agenda personal o de trabajo.'),
    ('h3', 'Opción B — Un calendario nuevo dedicado al bot (más limpio)'),
    ('p', 'Crea un calendario separado solo para citas del bot. Así no se mezclan con tus eventos personales. <b>Recomendamos opción B</b> para clientes con muchas citas.'),
    ('h3', 'Opción C — TicoSys hospeda el calendario (si no quieres compartir nada tuyo)'),
    ('p', 'Si por política de privacidad no quieres compartir tu Calendar con nadie, podemos crear el calendario bajo nuestra cuenta y compartírtelo a ti. <b>Avísanos por email</b> y lo coordinamos.'),
    ('h2', 'Pasos para Opción A (calendario principal)'),
    ('olist', [
        'Ve a <b>https://calendar.google.com</b>',
        'En el panel izquierdo, busca tu calendario principal (suele tener tu nombre)',
        'Pasa el ratón por encima → click en los <b>3 puntos</b> → <b>"Configuración y uso compartido"</b>',
        'Baja a la sección <b>"Compartir con personas concretas"</b>',
        'Click <b>"Añadir personas"</b>',
        'Email: <b>ticosysinfo@gmail.com</b>',
        'Permisos: <b>"Realizar cambios en eventos"</b> (esto es necesario para crear citas)',
        'Click <b>"Enviar"</b>',
    ]),
    ('p', 'Ya está. Tu <b>Calendar ID</b> será: <font face="Courier">primary</font> o el email asociado al calendario.'),
    ('h2', 'Pasos para Opción B (calendario nuevo)'),
    ('olist', [
        'Ve a <b>https://calendar.google.com</b>',
        'En el panel izquierdo, junto a "Otros calendarios", click en el <b>"+"</b>',
        '<b>"Crear calendario nuevo"</b>',
        'Nombre: ej. <i>Citas Bot — [Tu Negocio]</i>',
        'Descripción opcional · Zona horaria correcta',
        'Click <b>"Crear calendario"</b>',
        'En el panel izquierdo, busca el calendario recién creado',
        'Pasa el ratón → 3 puntos → <b>"Configuración y uso compartido"</b>',
        '<b>"Compartir con personas concretas"</b> → <b>"Añadir personas"</b>',
        'Email: <b>ticosysinfo@gmail.com</b>',
        'Permisos: <b>"Realizar cambios en eventos"</b>',
        'Click <b>"Enviar"</b>',
        'En la misma pantalla, baja hasta <b>"Integrar calendario"</b>',
        'Copia el campo <b>"ID de calendario"</b> — algo como <font face="Courier">abc123@group.calendar.google.com</font>',
    ]),
    ('callout', '<b>¿Por qué ticosysinfo@gmail.com y no info@ticosys.com?</b> La cuenta de Google que el bot usa internamente para acceder a Calendar y Drive se llama así. Si compartes con otra dirección distinta, el bot no podrá leer ni escribir.'),
    ('h2', 'Enviarnos los datos'),
    ('p', 'Mándanos un email a <b>info@ticosys.com</b> con asunto <b>"Calendar ID — [tu empresa]"</b>:'),
    ('code', 'Asunto: Calendar ID — [tu empresa]\n\nMi Calendar ID es: [pega aquí]\n\nHorario en que quiero que el bot acepte citas:\n- Lunes a Viernes: 10:00 a 18:00\n- Sábados: 10:00 a 14:00\n- Duración de cada cita: 30 minutos (o 45, o 60...)\n- Tiempo entre citas: 15 minutos (opcional, para descanso entre clientes)'),
    ('h2', 'Sobre el enlace de Google Meet'),
    ('p', 'Cada cita que agenda el bot incluye <b>automáticamente</b> un enlace de videollamada de Google Meet (lo genera Google al crear el evento). El cliente:'),
    ('list', [
        'Recibe el email de confirmación con el enlace de Meet',
        'Recibe la invitación de Google Calendar a su correo (con un botón "Unirse a Google Meet")',
        'Recibe un recordatorio 1 hora antes',
    ]),
    ('p', 'No tienes que crear las videollamadas a mano — Google las prepara solo. Solo tienes que entrar a la videollamada a la hora pactada.'),
    ('h2', '¿Y si quiero cambiar horarios después?'),
    ('p', 'Avísanos por email y los ajustamos en tu workflow. Cambio en directo, sin caída de servicio.'),
    ('h2', 'Si el bot no agenda'),
    ('p', 'Posibles causas:'),
    ('olist', [
        '<b>No compartiste el calendario</b> con ticosysinfo@gmail.com (o lo compartiste solo con permisos de lectura, no de escritura)',
        '<b>El Calendar ID que enviaste es incorrecto</b> (el principal es siempre el email; el de calendarios nuevos termina en @group.calendar.google.com)',
        '<b>No has indicado horarios</b> — el bot no sabe cuándo aceptar citas',
    ]),
    ('p', '<b>¿Dudas?</b> Escribe a info@ticosys.com'),
]

# =====================================================================
# GUIA 04 - Google Drive (FIX: ticosysinfo@gmail.com)
# =====================================================================
guia_04 = [
    ('p', 'Para que tu bot pueda <b>enviar imágenes, PDFs, videos</b> o cualquier archivo a tus clientes en respuesta a sus mensajes, necesita acceso a una carpeta de Google Drive donde tú subes esos archivos.'),
    ('p', '<b>Tiempo total:</b> 3 minutos.'),
    ('h2', '¿Cómo funciona?'),
    ('olist', [
        'Tú creas una carpeta en tu Drive con archivos como <font face="Courier">precios-2026.pdf</font>, <font face="Courier">demo-servicio.mp4</font>, <font face="Courier">mapa-ubicacion.jpg</font>',
        'El bot, cuando un cliente le pide algo (ej. "envíame la lista de precios"), busca por palabras clave en los nombres de los archivos',
        'Cuando encuentra uno, lo descarga y se lo envía al cliente en el chat',
    ]),
    ('h2', 'PASO 1 — Crear la carpeta'),
    ('olist', [
        'Ve a <b>https://drive.google.com</b>',
        'Click derecho → <b>"Nueva carpeta"</b>',
        'Nombre: <i>Archivos Bot — [tu negocio]</i> (o como quieras)',
        'Click <b>"Crear"</b>',
    ]),
    ('h2', 'PASO 2 — Compartir con TicoSys'),
    ('olist', [
        'Click derecho en la carpeta → <b>"Compartir"</b>',
        'En "Añadir personas y grupos", escribe: <b>ticosysinfo@gmail.com</b>',
        'Permisos: <b>"Lector"</b> (con esto basta — el bot solo lee/descarga)',
        '<b>Desmarca</b> "Notificar a las personas" (no es necesario)',
        'Click <b>"Compartir"</b>',
    ]),
    ('callout', '<b>¿Por qué ticosysinfo@gmail.com?</b> Es la cuenta de Google que el bot usa internamente para acceder a Drive. Si compartes con otra dirección distinta, el bot no podrá leer los archivos.'),
    ('h2', 'PASO 3 — Obtener el ID de la carpeta'),
    ('olist', [
        'Entra a la carpeta haciendo doble click',
        'Mira la URL en el navegador. Es algo como:',
    ]),
    ('code', 'https://drive.google.com/drive/folders/1u__pLGtj-4y66rORS7gR2Y8qgybU6l1t'),
    ('p', 'El <b>Folder ID</b> es la parte después de <font face="Courier">/folders/</font>:'),
    ('code', '1u__pLGtj-4y66rORS7gR2Y8qgybU6l1t'),
    ('p', 'Cópialo y envíanoslo a <b>info@ticosys.com</b>'),
    ('h2', 'PASO 4 — Subir tus archivos'),
    ('p', 'Las reglas para que el bot los encuentre bien:'),
    ('h3', 'Nombres descriptivos con guiones'),
    ('p', '<b>BIEN:</b>'),
    ('list', [
        '<font face="Courier">lista-precios-2026.pdf</font>',
        '<font face="Courier">demo-servicio-tarot.mp4</font>',
        '<font face="Courier">mapa-como-llegar.jpg</font>',
        '<font face="Courier">formulario-reservas.pdf</font>',
        '<font face="Courier">garantia-devoluciones.pdf</font>',
    ]),
    ('p', '<b>MAL:</b>'),
    ('list', [
        '<font face="Courier">IMG_20260315.jpg</font> (¿qué es?)',
        '<font face="Courier">documento.pdf</font> (¿de qué?)',
        '<font face="Courier">archivo final FINAL v2.docx</font> (espacios y nombres confusos)',
    ]),
    ('h3', 'Por qué importan los nombres'),
    ('p', 'El bot busca palabras clave en el nombre del archivo. Si el cliente dice:'),
    ('list', [
        '<i>"¿Me puedes enviar tus precios?"</i> → el bot busca un archivo con <b>precios</b> en el nombre',
        '<i>"¿Cómo llego a la tienda?"</i> → busca <b>mapa</b> o <b>ubicacion</b> o <b>como-llegar</b>',
    ]),
    ('p', 'Cuanto más descriptivo el nombre, mejor responde el bot.'),
    ('h2', 'Formatos soportados'),
    ('list', [
        '<b>Imágenes:</b> .jpg, .png, .gif, .webp',
        '<b>Videos:</b> .mp4, .mov (hasta 16 MB por WhatsApp; hasta 50 MB por Telegram)',
        '<b>Documentos:</b> .pdf, .docx, .xlsx',
        '<b>Otros:</b> .txt, .csv',
    ]),
    ('callout', '<b>Tamaño máximo por archivo:</b> 100 MB. Pero ojo a los límites por canal: WhatsApp 16 MB / Telegram 50 MB / web sin límite práctico.'),
    ('h2', 'Ejemplos prácticos por sector'),
    ('h3', 'Tarot / Esoterismo'),
    ('list', [
        '<font face="Courier">precios-consultas.pdf</font>',
        '<font face="Courier">que-es-tarot-explicacion.jpg</font>',
        '<font face="Courier">como-funciona-la-consulta-online.pdf</font>',
        '<font face="Courier">testimonios-clientes.pdf</font>',
    ]),
    ('h3', 'Restaurante'),
    ('list', [
        '<font face="Courier">carta-2026.pdf</font>',
        '<font face="Courier">menu-del-dia.pdf</font>',
        '<font face="Courier">mapa-ubicacion.jpg</font>',
        '<font face="Courier">politica-reservas.pdf</font>',
    ]),
    ('h3', 'Servicios profesionales'),
    ('list', [
        '<font face="Courier">lista-servicios-precios.xlsx</font>',
        '<font face="Courier">casos-de-exito.pdf</font>',
        '<font face="Courier">proceso-trabajo.pdf</font>',
        '<font face="Courier">presupuesto-tipo.pdf</font>',
    ]),
    ('h2', '¿Puedo añadir más archivos después?'),
    ('p', 'Sí, en cualquier momento. Solo sube nuevos archivos a la misma carpeta de Drive. <b>No necesitas avisarnos</b> — el bot los detecta automáticamente la próxima vez que un cliente pida algo relacionado.'),
    ('h2', 'Si el bot no encuentra los archivos'),
    ('olist', [
        'Verifica que <b>compartiste la carpeta con ticosysinfo@gmail.com</b> con permisos de Lector',
        'Verifica que enviaste el <b>Folder ID correcto</b>',
        'Revisa el <b>nombre de los archivos</b> — si nadie usaría esas palabras clave, el bot no los encontrará',
    ]),
    ('p', '<b>¿Dudas?</b> Escribe a info@ticosys.com'),
]

# =====================================================================
# GUIA 05 - Emails desde tu dominio
# =====================================================================
guia_05 = [
    ('p', 'El bot envía emails a tus clientes en varios momentos:'),
    ('list', [
        '<b>Confirmación de cita</b> (cuando agenda una)',
        '<b>Recordatorio</b> (1h antes de la cita)',
        '<b>Seguimiento de leads</b> (a las 24h si el cliente quedó interesado pero no compró)',
        '<b>Resumen diario</b> (a ti, con la actividad del día)',
    ]),
    ('p', 'Por defecto estos emails salen desde <font face="Courier">info@ticosys.com</font>. Si quieres que salgan desde tu propio email (ej: <font face="Courier">info@tuempresa.com</font> o <font face="Courier">tunombre@gmail.com</font>), sigue esta guía.'),
    ('h2', '¿Por qué querrías cambiarlo?'),
    ('list', [
        '<b>Profesionalismo</b> — el cliente recibe el email "de ti", no de un tercero',
        '<b>Reconocimiento de marca</b>',
        '<b>Mejor tasa de apertura</b> (los clientes confían más)',
    ]),
    ('h2', 'Opción A — Gmail / Google Workspace (la más común)'),
    ('h3', 'Paso 1 — Activa la verificación en 2 pasos (si no la tienes)'),
    ('olist', [
        'Ve a <b>https://myaccount.google.com/security</b>',
        'Busca "Verificación en 2 pasos" → actívala si está OFF',
        'Sin esto, el siguiente paso no aparecerá',
    ]),
    ('h3', 'Paso 2 — Genera una "Contraseña de aplicación"'),
    ('olist', [
        'Ve a <b>https://myaccount.google.com/apppasswords</b>',
        'En "Nombre" escribe: <i>Bot TicoSys</i>',
        'Click <b>"Crear"</b>',
        'Te muestra una contraseña de 16 caracteres como <font face="Courier">abcd efgh ijkl mnop</font>',
        '<b>Cópiala completa, sin los espacios</b> → quedaría: <font face="Courier">abcdefghijklmnop</font>',
    ]),
    ('callout', '<b>Importante:</b> esta NO es tu contraseña de Gmail. Es una "contraseña especial" que solo TicoSys usará para enviar emails en tu nombre. Si en algún momento quieres revocarla, vuelves a esa pantalla y la eliminas.'),
    ('h3', 'Paso 3 — Envíanos los datos'),
    ('p', 'Envía un email a <b>info@ticosys.com</b> con asunto <b>"Email SMTP — [tu empresa]"</b>:'),
    ('code', 'Email remitente: tunombre@gmail.com\nContraseña de app generada: abcdefghijklmnop\n\nQuiero que los emails del bot salgan desde este correo.'),
    ('h3', '¿Qué pasará después?'),
    ('list', [
        'Si nos envías estos datos <b>antes</b> del alta de tu cuenta: los configuramos directamente en tu workflow desde el inicio',
        'Si nos los envías <b>después</b> del alta: actualizamos tu workflow en n8n para que use tus credenciales SMTP (5 minutos)',
        'Si <b>nunca los envías</b>: los emails del bot saldrán desde <font face="Courier">info@ticosys.com</font> con tu nombre como remitente (funcional, pero menos profesional)',
    ]),
    ('h2', 'Opción B — Email corporativo (no-Gmail)'),
    ('p', 'Si usas un email tipo <font face="Courier">info@miempresa.com</font> con dominio propio (no de Google), necesitas los datos de tu <b>servidor SMTP</b>:'),
    ('h3', 'Datos que necesitamos'),
    ('olist', [
        '<b>Email remitente:</b> info@tuempresa.com',
        '<b>Servidor SMTP:</b> ej. smtp.tuempresa.com o mail.tuempresa.com',
        '<b>Puerto SMTP:</b> típicamente 587 (TLS) o 465 (SSL)',
        '<b>Usuario SMTP:</b> normalmente tu email completo',
        '<b>Contraseña SMTP:</b> la contraseña del email',
    ]),
    ('h3', 'Dónde conseguirlos'),
    ('p', 'Te los da tu <b>proveedor de hosting / correo</b>:'),
    ('list', [
        'Si usas <b>cPanel</b>: Email Accounts → Connect Devices → Email Application Manual Settings',
        'Si usas <b>Outlook 365</b>: support.microsoft.com → "Configuración de POP, IMAP y SMTP"',
        'Si usas <b>Zoho Mail</b>: zoho.com/mail/help/zoho-smtp.html',
        'Si <b>no sabes</b>, pregunta a tu administrador de hosting',
    ]),
    ('h3', 'Envíanos los datos'),
    ('p', 'Email a <b>info@ticosys.com</b> con asunto <b>"Email SMTP — [tu empresa]"</b>:'),
    ('code', 'Email remitente: info@miempresa.com\nServidor SMTP: smtp.miempresa.com\nPuerto: 587\nUsuario: info@miempresa.com\nContraseña: [la contraseña]'),
    ('h2', 'Seguridad'),
    ('list', [
        '<b>Tu contraseña queda guardada en n8n</b> (el motor de workflows que usa TicoSys), <b>encriptada</b>',
        '<b>Solo se usa para enviar emails desde tu cuenta</b> — no leemos tus emails, no enviamos sin tu permiso',
        '<b>Cuándo TicoSys envía emails:</b> confirmación de cita / recordatorio / seguimiento / resumen diario. Nada más.',
        '<b>Si en cualquier momento quieres revocar el acceso:</b> elimina la "contraseña de app" en tu Gmail y avísanos para actualizar.',
    ]),
    ('h2', '¿Cuándo entrará en vigor el cambio?'),
    ('p', 'En las <b>24 horas</b> siguientes a recibir tus datos:'),
    ('list', [
        'Configuramos tu SMTP en el workflow del bot',
        'Hacemos una prueba enviando un email de test',
        'Te confirmamos cuando esté funcionando',
    ]),
    ('h2', 'Errores comunes'),
    ('table', {
        'rows': [
            ['Problema', 'Solución'],
            ['"No aparece la opción de Contraseña de aplicación"', 'No has activado la verificación en 2 pasos en tu cuenta de Google. Actívala primero.'],
            ['"Email rechazado por el servidor"', 'Contraseña incorrecta, o el servidor SMTP requiere autenticación distinta. Verifica con tu proveedor.'],
            ['"Gmail bloqueó el envío"', 'Gmail detectó actividad sospechosa. Entra en tu Gmail → revisa "Actividad reciente" → marca como "Yo fui"'],
        ],
        'col_widths': [70 * mm, 110 * mm],
    }),
    ('h2', 'Si decides NO cambiar el remitente'),
    ('p', 'No pasa nada. Los emails siguen saliendo desde <font face="Courier">info@ticosys.com</font> con tu nombre como firma. Es funcional aunque menos personalizado.'),
    ('p', '<b>¿Dudas?</b> Escribe a info@ticosys.com'),
]

# =====================================================================
# GENERAR TODOS
# =====================================================================
print('Generando guías PDF con nuevo branding TicoSys...')
make_pdf('00_Bienvenida_y_Primeros_Pasos.pdf',
         'Bienvenido a TicoSys — Primeros pasos', guia_00)
make_pdf('01_Documentos_para_el_Bot.pdf',
         'Guía: Documentos para el Bot', guia_01)
make_pdf('02_Conectar_WhatsApp_Business.pdf',
         'Guía: Conectar WhatsApp Business con tu bot', guia_02)
make_pdf('02b_Conectar_Telegram.pdf',
         'Guía: Conectar Telegram con tu bot (5 minutos)', guia_02b)
make_pdf('03_Compartir_Google_Calendar.pdf',
         'Guía: Compartir tu Google Calendar con el bot', guia_03)
make_pdf('04_Compartir_Google_Drive.pdf',
         'Guía: Compartir Google Drive con el bot', guia_04)
make_pdf('05_Emails_Desde_Tu_Dominio.pdf',
         'Guía: Emails automáticos desde TU dominio', guia_05)
print('Listo.')
