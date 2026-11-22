"""Textos legales de VRPC (aviso legal y política de cookies).

Rellena los datos de DATOS (None = pendiente). Mientras alguno siga en None, aparece resaltado en la web
como «[PENDIENTE: ...]» y build.py avisa por consola. Cuando estén todos, las páginas quedan limpias.
Los textos siguen la LSSI-CE (art. 10 y 22.2), el RGPD y la LOPDGDD. Conviene que Jose o su gestor
los revise antes del lanzamiento: esto no sustituye el asesoramiento jurídico.
"""
import html

E = html.escape
FECHA = "22 de noviembre de 2026"

DATOS = {
    "nombre": None,       # Nombre y apellidos del autónomo o razón social de la empresa
    "nif": None,          # NIF / CIF
    "registro": None,     # Datos de inscripción en el Registro Mercantil (solo si es sociedad; poner "No aplica" si es autónomo)
    "hosting": None,      # Proveedor de alojamiento web (p. ej. GitHub Pages / el que se contrate el día del lanzamiento)
    "domicilio": "Carrer de les Aigües del Llobregat, 115, interior, 08906 L'Hospitalet de Llobregat (Barcelona)",
    "email": "info@ventareparacionpc.es",
    "telefono": "622 22 97 95",
    "web": "https://ventareparacionpc.es",
    "marca": "VentaReparacionPC",
}
ETIQUETAS = {
    "nombre": "nombre y apellidos o razón social del titular",
    "nif": "NIF/CIF del titular",
    "registro": "datos del Registro Mercantil (o «No aplica»)",
    "hosting": "proveedor de alojamiento web",
}
PENDIENTES = []


def d(clave):
    """Devuelve el dato escapado o una marca visible si falta."""
    v = DATOS.get(clave)
    if v:
        return E(v)
    if clave not in PENDIENTES:
        PENDIENTES.append(clave)
    return f'<mark class="pend">[PENDIENTE: {ETIQUETAS[clave]}]</mark>'


def aviso_legal():
    return f"""<section class="wrap sec"><div class="card box legal">
<p class="upd">Última actualización: {FECHA}</p>

<h2>1. Datos identificativos del titular</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de que el sitio web <strong>{E(DATOS['web'])}</strong> (en adelante, la «Web») pertenece a:</p>
<ul>
<li><strong>Titular:</strong> {d('nombre')}</li>
<li><strong>Nombre comercial:</strong> {E(DATOS['marca'])}</li>
<li><strong>NIF/CIF:</strong> {d('nif')}</li>
<li><strong>Domicilio:</strong> {d_dom()}</li>
<li><strong>Correo electrónico:</strong> <a href="mailto:{E(DATOS['email'])}">{E(DATOS['email'])}</a></li>
<li><strong>Teléfono:</strong> {E(DATOS['telefono'])}</li>
<li><strong>Inscripción registral:</strong> {d('registro')}</li>
<li><strong>Actividad:</strong> servicio técnico informático: reparación, mantenimiento, actualización y montaje de ordenadores, y asesoramiento sobre equipos PC Gaming.</li>
</ul>

<h2>2. Objeto y condiciones de uso</h2>
<p>La Web tiene por objeto informar sobre los servicios del taller y facilitar el contacto con el titular. El acceso es libre y gratuito y atribuye la condición de usuario, que se compromete a hacer un uso adecuado de la Web conforme a la ley, la buena fe y el orden público, y a no emplearla para fines ilícitos o lesivos para el titular o terceros.</p>

<h2>3. Información sobre equipos y precios</h2>
<p>Los equipos PC Gaming y los precios que se muestran en la Web son <strong>orientativos y de referencia</strong>. No constituyen una oferta vinculante ni permiten la compra en línea. Las configuraciones, la disponibilidad y los precios definitivos se confirman con el titular, directamente y por los medios de contacto indicados, antes de cualquier contratación. Las características pueden cambiar sin previo aviso por razones de disponibilidad de componentes.</p>

<h2>4. Propiedad intelectual e industrial</h2>
<p>Los textos, el diseño, el código y los elementos gráficos de la Web pertenecen al titular o se utilizan con la debida autorización, y están protegidos por la normativa de propiedad intelectual e industrial. No se permite su reproducción, distribución o transformación sin autorización expresa. Las marcas, nombres comerciales e imágenes de productos de terceros (fabricantes de procesadores, tarjetas gráficas, cajas u otros componentes) pertenecen a sus respectivos propietarios y se muestran únicamente con fines informativos.</p>

<h2>5. Responsabilidad</h2>
<p>El titular procura que la información de la Web sea exacta y esté actualizada, pero no garantiza la ausencia de errores ni la disponibilidad continua del sitio, y no se responsabiliza de los daños derivados de interrupciones, fallos técnicos o del uso indebido de la Web. Tampoco responde de los contenidos de sitios de terceros a los que se pueda acceder mediante enlaces.</p>

<h2>6. Enlaces a terceros</h2>
<p>La Web puede incluir enlaces a servicios externos, como Google Maps (ubicación y valoraciones) o WhatsApp (contacto). Esos servicios se rigen por sus propias condiciones y políticas de privacidad, ajenas al titular. Se recomienda revisarlas antes de utilizarlos.</p>

<h2>7. Protección de datos personales</h2>
<p>De acuerdo con el Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD), se informa de lo siguiente:</p>
<ul>
<li><strong>Responsable del tratamiento:</strong> el titular indicado en el apartado 1.</li>
<li><strong>Finalidad:</strong> atender las consultas, solicitudes de cita y presupuesto que el usuario envíe por teléfono, WhatsApp o correo electrónico, y gestionar, en su caso, la prestación del servicio contratado.</li>
<li><strong>Base jurídica:</strong> el consentimiento del usuario al contactar y la aplicación de medidas precontractuales o la ejecución del contrato de servicio.</li>
<li><strong>Datos tratados:</strong> los que el usuario facilite voluntariamente (nombre, teléfono, correo y datos del equipo o de la incidencia). La Web no dispone de formularios que almacenen datos.</li>
<li><strong>Conservación:</strong> durante el tiempo necesario para atender la solicitud y, después, durante los plazos legales aplicables (por ejemplo, fiscales y de garantía).</li>
<li><strong>Destinatarios:</strong> no se ceden datos a terceros salvo obligación legal. Si se utiliza WhatsApp, los datos se tratan además conforme a las condiciones de ese servicio.</li>
<li><strong>Derechos:</strong> acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad, escribiendo a <a href="mailto:{E(DATOS['email'])}">{E(DATOS['email'])}</a>, indicando el derecho que se quiere ejercer. Si considera que sus derechos no han sido atendidos, puede presentar una reclamación ante la Agencia Española de Protección de Datos (www.aepd.es).</li>
</ul>
<p>Cuando el usuario entregue un equipo para su reparación, el titular tratará los datos y la información que contenga únicamente en la medida necesaria para el servicio, con confidencialidad y sin copiarlos ni conservarlos salvo petición expresa del cliente.</p>

<h2>8. Alojamiento</h2>
<p>La Web se aloja en los servidores de: {d('hosting')}. Es posible que el proveedor registre datos técnicos de conexión (como la dirección IP) por motivos de seguridad y funcionamiento.</p>

<h2>9. Legislación aplicable y jurisdicción</h2>
<p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales que correspondan conforme a la normativa vigente; si el usuario tiene la condición de consumidor, serán los de su domicilio cuando así lo establezca la ley.</p>

<h2>10. Modificaciones</h2>
<p>El titular puede modificar este aviso legal para adaptarlo a cambios normativos o del servicio. La versión vigente es la publicada en esta página, con su fecha de actualización.</p>
</div></section>"""


def d_dom():
    return E(DATOS["domicilio"])


def cookies():
    return f"""<section class="wrap sec"><div class="card box legal">
<p class="upd">Última actualización: {FECHA}</p>

<h2>1. ¿Qué son las cookies?</h2>
<p>Las cookies son pequeños archivos que un sitio web guarda en el navegador o el dispositivo del usuario para recordar información sobre su visita. Pueden ser propias (las instala el sitio que se visita) o de terceros (las instala otro servicio), y técnicas, de personalización, de análisis o publicitarias.</p>

<h2>2. ¿Qué cookies utiliza esta web?</h2>
<p><strong>Esta web no utiliza cookies propias ni de terceros</strong> y no instala en el dispositivo del usuario ninguna herramienta de seguimiento, análisis o publicidad. Por ese motivo no muestra un aviso de consentimiento de cookies, conforme al artículo 22.2 de la LSSI-CE.</p>
<p>La Web contiene enlaces a servicios externos (Google Maps, WhatsApp). Esos servicios son ajenos a la Web: solo se activan si el usuario sigue el enlace y se rigen por sus propias políticas de cookies y de privacidad.</p>

<h2>3. Datos técnicos de conexión</h2>
<p>Como en cualquier sitio web, el servidor donde se aloja la Web ({d('hosting')}) puede registrar de forma automática datos técnicos de la conexión, como la dirección IP, el navegador o la fecha y hora de acceso, necesarios para el funcionamiento y la seguridad del servicio. No se utilizan para identificar a los usuarios ni para elaborar perfiles.</p>

<h2>4. ¿Cómo gestionar o eliminar cookies en el navegador?</h2>
<p>Aunque esta Web no instala cookies, el usuario puede configurar su navegador para aceptarlas, rechazarlas o eliminarlas en cualquier momento, y consultar o borrar las que haya almacenado otros sitios. Cada navegador (Chrome, Edge, Firefox, Safari y otros) ofrece esas opciones en su apartado de privacidad o configuración.</p>

<h2>5. Cambios en esta política</h2>
<p>Si en el futuro la Web incorporase cookies u otras tecnologías similares (por ejemplo, herramientas de analítica), esta política se actualizará antes y se solicitará el consentimiento del usuario cuando la ley lo exija.</p>

<h2>6. Más información</h2>
<p>Para cualquier duda sobre esta política, puede escribir a <a href="mailto:{E(DATOS['email'])}">{E(DATOS['email'])}</a>. Consulte también el <a href="aviso-legal.html">aviso legal</a> de la Web.</p>
</div></section>"""
