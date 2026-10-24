/**
 * Interfaz del MVP: inicio de sesión, navegación, tema y extracción.
 *
 * Cubre RF-00 (autenticación privada), RF-01 (carga), RF-02 (extracción),
 * RF-03 (clasificación local y determinista), RF-04 (análisis de cláusulas
 * con IA local, prototipo), RF-06 (interfaz en español) y RF-07
 * (navegación principal y tema claro / oscuro). No envía contratos a
 * servicios externos: el análisis usa solo el servidor local en loopback.
 *
 * Navegación (RF-07.1): tras iniciar sesión hay cuatro secciones, Inicio,
 * Analizar contrato, Resultados e Historial. La carga y extracción ocurren en Analizar contrato.
 * Resultados muestra los hallazgos del último análisis; Historial lista los análisis anteriores.
 *
 * Tema (RF-07.2 a RF-07.5): control claro/oscuro en la barra superior. La
 * preferencia se guarda en localStorage y se restaura al recargar; sin
 * preferencia se usa el tema del sistema. Cambiarlo no cierra la sesión ni
 * borra el trabajo: solo cambia el atributo data-tema en <html>.
 *
 * Autenticación: al abrir se consulta GET /yo; solo con sesión válida se
 * muestra la navegación. El login usa los campos del backend (usuario,
 * contrasena) y la sesión viaja en cookie HttpOnly: el navegador nunca
 * guarda contraseñas ni tokens. Sin registro público (RF-00.2).
 *
 * Llamadas a rutas relativas; el dev server las redirige al backend
 * (ver vite.config.ts), así que no hace falta CORS.
 */

import { useEffect, useRef, useState } from 'react'
import './App.css'

/** Formatos aceptados por el backend, según RF-01.1 y RF-01.2. */
const EXTENSIONES_ACEPTADAS = ['.pdf', '.docx']

interface RespuestaSesion {
  ok: boolean
  usuario: string | null
  codigo: string | null
  motivo: string | null
}

interface RespuestaExtraccion {
  ok: boolean
  texto: string | null
  formato: string | null
  num_paginas: number | null
  codigo: string | null
  motivo: string | null
}

interface RespuestaClasificacion {
  ok: boolean
  tipo: string | null
  etiqueta: string | null
  confianza: string | null
  evidencias: string[] | null
  motivo: string | null
}

interface HallazgoAnalisis {
  tipo: string
  categoria: string
  descripcion: string
  cita: string
  explicacion: string
  consecuencia: string
  recomendacion: string
  limitaciones: string
}

interface RespuestaAnalisis {
  ok: boolean
  hallazgos: HallazgoAnalisis[] | null
  num_descartados: number
  codigo: string | null
  motivo: string | null
}

interface RespuestaEstadoAnalisis {
  ocupado: boolean
  fuente: string
}

interface RegistroHistorial {
  id: number
  fecha: string
  tipo_confirmado: string
  num_hallazgos: number
  hallazgos: HallazgoAnalisis[]
}

const ETIQUETAS_HALLAZGO: Record<string, string> = {
  ambiguedad: 'Posible ambigüedad',
  omision: 'Posible omisión',
  contradiccion: 'Posible contradicción',
  riesgo: 'Posible riesgo',
}

function etiquetaHallazgo(tipo: string): string {
  return ETIQUETAS_HALLAZGO[tipo] ?? tipo
}

function formatearFechaLocal(fechaISO: string): string {
  if (!fechaISO) return ''
  try {
    const fecha = new Date(fechaISO)
    if (isNaN(fecha.getTime())) return fechaISO
    return fecha.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch {
    return fechaISO
  }
}

interface HallazgoProps {
  hallazgo: HallazgoAnalisis
}

function Hallazgo({ hallazgo }: HallazgoProps) {
  return (
    <li>
      <p>
        <strong>{etiquetaHallazgo(hallazgo.tipo)}</strong>{' — '}
        {hallazgo.categoria}
      </p>
      <p>{hallazgo.descripcion}</p>
      {hallazgo.cita && <blockquote>“{hallazgo.cita}”</blockquote>}
      <p>
        <strong>Explicación:</strong>{' '}
        {hallazgo.explicacion}
      </p>
      <p>
        <strong>Posible consecuencia:</strong>{' '}
        {hallazgo.consecuencia}
      </p>
      <p>
        <strong>Recomendación:</strong>{' '}
        {hallazgo.recomendacion}
      </p>
      <p className="sugerencia">
        <strong>Limitaciones:</strong>{' '}
        {hallazgo.limitaciones}
      </p>
    </li>
  )
}

type TipoOpcion = 'prestacion_de_servicios' | 'proveedor'

const OPCIONES_TIPO: { id: TipoOpcion; etiqueta: string }[] = [
  { id: 'prestacion_de_servicios', etiqueta: 'Prestación de servicios' },
  { id: 'proveedor', etiqueta: 'Contrato de proveedor' },
]

function etiquetaDe(tipo: TipoOpcion | null): string {
  if (!tipo) return ''
  const opcion = OPCIONES_TIPO.find((o) => o.id === tipo)
  return opcion ? opcion.etiqueta : ''
}

/**
 * Deduplica las evidencias de la propuesta (RF-03.2).
 *
 * Cada evidencia es un fragmento literal del texto extraído, así que basta
 * con buscarla con indexOf para conocer su posición exacta. Se descartan los
 * duplicados y los fragmentos cuyo intervalo se solape con otro más largo
 * (la señal queda cubierta por la ventana mayor, que aporta más contexto).
 * El resultado sigue siendo literal y ya no contiene solapes.
 */
function deduplicarEvidencias(
  texto: string | null,
  evidencias: string[],
): string[] {
  const unicas = evidencias.filter((e, i, arr) => arr.indexOf(e) === i)
  if (!texto) return unicas

  const localizadas = unicas.map((fragmento) => {
    const inicio = texto.indexOf(fragmento)
    return {
      fragmento,
      inicio,
      fin: inicio === -1 ? -1 : inicio + fragmento.length,
    }
  })

  // De mayor a menor: la ventana más larga tiene prioridad.
  const ordenadas = [...localizadas].sort(
    (a, b) => b.fragmento.length - a.fragmento.length,
  )
  const mantenidas: typeof ordenadas = []
  for (const candidata of ordenadas) {
    if (candidata.inicio === -1) {
      // No aparece en el texto (no debería pasar): se conserva tal cual.
      mantenidas.push(candidata)
      continue
    }
    const solapa = mantenidas.some(
      (m) =>
        m.inicio !== -1 &&
        candidata.inicio < m.fin &&
        m.inicio < candidata.fin,
    )
    if (!solapa) mantenidas.push(candidata)
  }

  // Se devuelven en el orden en que aparecen en el documento.
  return mantenidas
    .sort((a, b) => a.inicio - b.inicio)
    .map((m) => m.fragmento)
}

type Sesion = 'consultando' | 'sin-sesion' | 'activa'
type Estado = 'inicio' | 'cargando' | 'exito' | 'error'

/** Secciones de la navegación principal (RF-07.1). */
type Vista = 'inicio' | 'analizar' | 'resultados' | 'historial'

const VISTAS: { id: Vista; etiqueta: string }[] = [
  { id: 'inicio', etiqueta: 'Inicio' },
  { id: 'analizar', etiqueta: 'Analizar contrato' },
  { id: 'resultados', etiqueta: 'Resultados' },
  { id: 'historial', etiqueta: 'Historial' },
]

/** Temas disponibles (RF-07.2). */
type Tema = 'claro' | 'oscuro'

/** Clave de localStorage para la preferencia de tema (RF-07.3). */
const CLAVE_TEMA = 'mrl-tema'

function leerTemaInicial(): Tema {
  try {
    const guardado = window.localStorage.getItem(CLAVE_TEMA)
    if (guardado === 'claro' || guardado === 'oscuro') return guardado
  } catch {
    // Sin acceso al almacenamiento (modo privado): se usa el sistema.
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'oscuro'
    : 'claro'
}

function extensionDe(nombre: string): string {
  const punto = nombre.lastIndexOf('.')
  return punto === -1 ? '' : nombre.slice(punto).toLowerCase()
}

function tamanoLegible(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function App() {
  const [sesion, setSesion] = useState<Sesion>('consultando')
  const [usuario, setUsuario] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [clave, setClave] = useState('')
  const [entrando, setEntrando] = useState(false)
  const [errorLogin, setErrorLogin] = useState<string | null>(null)

  // Navegación principal y tema (RF-07). Ambos viven en el estado de React:
  // cambiar de vista o de tema no toca la sesión ni el trabajo en curso.
  const [vista, setVista] = useState<Vista>('inicio')
  const [tema, setTema] = useState<Tema>(leerTemaInicial)

  const [archivo, setArchivo] = useState<File | null>(null)
  const [avisoArchivo, setAvisoArchivo] = useState<string | null>(null)
  const [estado, setEstado] = useState<Estado>('inicio')
  const [resultado, setResultado] = useState<RespuestaExtraccion | null>(null)
  const [mensajeError, setMensajeError] = useState<string | null>(null)

  // Clasificación del tipo de contrato (RF-03): propuesta del backend local,
  // selección corregible por el usuario y confirmación explícita.
  const [clasificacion, setClasificacion] = useState<RespuestaClasificacion | null>(null)
  const [tipoSeleccionado, setTipoSeleccionado] = useState<TipoOpcion | null>(null)
  const [confirmado, setConfirmado] = useState(false)
  const [analizando, setAnalizando] = useState(false)
  /** Limpia el estado del análisis RF-04 (respuestas tardías incluidas). */
  function reiniciarAnalisis() {
    idAnalisisRef.current += 1
    controladorAnalisisRef.current?.abort()
    controladorAnalisisRef.current = null
    setAnalizando(false)
    setHallazgos(null)
    setNumDescartados(0)
    setErrorAnalisis(null)
    setServidorOcupado(false)
  }

  /** Consulta si el servidor local sigue ocupado (sin prometer plazos). */
  async function consultarEstadoAnalisis(): Promise<void> {
    try {
      const respuesta = await fetch('/analizar-con-ia/estado')
      if (respuesta.status === 401) {
        volverALogin()
        return
      }
      const datos = (await respuesta.json()) as RespuestaEstadoAnalisis
      setServidorOcupado(datos.ocupado === true)
    } catch {
      setServidorOcupado(true)
    }
  }

  /** Carga el historial privado del usuario autenticado (GET /historial). */
  async function cargarHistorial(): Promise<void> {
    setCargandoHistorial(true)
    setErrorHistorial(null)
    try {
      const respuesta = await fetch('/historial')
      if (respuesta.status === 401) {
        volverALogin()
        return
      }
      let cuerpo: {
        ok: boolean
        registros: RegistroHistorial[] | null
        codigo: string | null
        motivo: string | null
      } | null = null
      try {
        cuerpo = (await respuesta.json()) as {
          ok: boolean
          registros: RegistroHistorial[] | null
          codigo: string | null
          motivo: string | null
        }
      } catch {
        cuerpo = null
      }
      if (!cuerpo || !cuerpo.ok) {
        setErrorHistorial(
          cuerpo?.motivo ?? 'No se pudo cargar el historial.',
        )
        return
      }
      setHistorial(cuerpo.registros ?? [])
    } catch {
      setErrorHistorial(
        'No se pudo conectar con el servidor para cargar el historial.',
      )
    } finally {
      setCargandoHistorial(false)
    }
  }

  /**
   * Analiza las cláusulas con IA local (RF-04, prototipo).
   *
   * Solo tras confirmar el tipo. La espera es cancelable con "Dejar de
   * esperar", que cierra la espera del cliente sin prometer que el
   * servidor detenga su generación: la respuesta tardía se descarta por
   * id de análisis y nunca se muestra para otro documento.
   */
  async function alAnalizarClausulas() {
    if (!resultado?.texto || !tipoSeleccionado || analizando) return
    const idAnalisis = idAnalisisRef.current + 1
    idAnalisisRef.current = idAnalisis
    const controlador = new AbortController()
    controladorAnalisisRef.current = controlador
    setAnalizando(true)
    setHallazgos(null)
    setNumDescartados(0)
    setErrorAnalisis(null)
    setServidorOcupado(false)
    try {
      const respuesta = await fetch('/analizar-con-ia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          texto: resultado.texto,
          tipo_confirmado: tipoSeleccionado,
        }),
        signal: controlador.signal,
      })
      if (respuesta.status === 401) {
        volverALogin()
        return
      }
      const datos = (await respuesta.json()) as RespuestaAnalisis
      if (idAnalisis !== idAnalisisRef.current) return
      if (!datos.ok) {
        setErrorAnalisis(datos.motivo ?? 'No se pudo completar el análisis.')
        await consultarEstadoAnalisis()
        return
      }
      setHallazgos(datos.hallazgos ?? [])
      setNumDescartados(datos.num_descartados ?? 0)
    } catch (error) {
      if (idAnalisis !== idAnalisisRef.current) return
      if (error instanceof DOMException && error.name === 'AbortError') {
        setErrorAnalisis(
          'Dejaste de esperar. El servidor local puede seguir procesando '
            + 'unos minutos; el resultado se descartará y no se mostrará.',
        )
        await consultarEstadoAnalisis()
        return
      }
      setErrorAnalisis(
        'No se pudo conectar con el servidor de análisis. '
          + 'Comprueba que el backend esté en marcha e inténtalo de nuevo.',
      )
      await consultarEstadoAnalisis()
    } finally {
      if (idAnalisis === idAnalisisRef.current) {
        controladorAnalisisRef.current = null
        setAnalizando(false)
      }
    }
  }

  /** Deja de esperar el análisis sin prometer que el servidor se detenga. */
  function alDejarDeEsperar() {
    controladorAnalisisRef.current?.abort()
  }

  const [hallazgos, setHallazgos] = useState<HallazgoAnalisis[] | null>(null)
  const [numDescartados, setNumDescartados] = useState(0)
  const [errorAnalisis, setErrorAnalisis] = useState<string | null>(null)
  const [servidorOcupado, setServidorOcupado] = useState(false)
  const [historial, setHistorial] = useState<RegistroHistorial[] | null>(null)
  const [cargandoHistorial, setCargandoHistorial] = useState(false)
  const [errorHistorial, setErrorHistorial] = useState<string | null>(null)
  const idAnalisisRef = useRef(0)
  const controladorAnalisisRef = useRef<AbortController | null>(null)
  const [clasificando, setClasificando] = useState(false)

  // Al abrir, la sesión vive en la cookie HttpOnly: se consulta al backend.
  useEffect(() => {
    let activa = true
    async function consultarSesion() {
      try {
        const respuesta = await fetch('/yo')
        let cuerpo: RespuestaSesion | null = null
    reiniciarAnalisis()

        try {
          cuerpo = (await respuesta.json()) as RespuestaSesion
        } catch {
          cuerpo = null
        }
        if (!activa) return
        if (respuesta.ok && cuerpo?.ok && cuerpo.usuario) {
          setUsuario(cuerpo.usuario)
          setSesion('activa')
        } else {
          setSesion('sin-sesion')
        }
      } catch {
        if (!activa) return
        setSesion('sin-sesion')
      }
    }
    void consultarSesion()
    return () => {
      activa = false
    }
  }, [])

  // Tema (RF-07.2 a RF-07.5): se aplica al documento y se guarda. Solo toca
  // el atributo visual y localStorage: la sesión y el trabajo siguen intactos.
  useEffect(() => {
    document.documentElement.setAttribute('data-tema', tema)
    try {
      window.localStorage.setItem(CLAVE_TEMA, tema)
    } catch {
      // Sin acceso al almacenamiento: el tema se aplica solo en memoria.
    }
  }, [tema])

  // Carga el historial privado al abrir la vista Historial con sesion activa.
  useEffect(() => {
    if (vista === 'historial' && sesion === 'activa') {
      void cargarHistorial()
    }
  }, [vista, sesion])

  function cambiarTema() {
    setTema((anterior) => (anterior === 'claro' ? 'oscuro' : 'claro'))
  }

  function volverALogin() {
    setSesion('sin-sesion')
    setUsuario(null)
    setClave('')
  }

  async function alIniciarSesion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (entrando) return
    setEntrando(true)
    reiniciarAnalisis()

    setErrorLogin(null)

    const datos = new FormData()
    datos.append('usuario', nombre.trim())
    datos.append('contrasena', clave)

    try {
      const respuesta = await fetch('/login', { method: 'POST', body: datos })
      let cuerpo: RespuestaSesion | null = null
      try {
        cuerpo = (await respuesta.json()) as RespuestaSesion
      } catch {
        cuerpo = null
    reiniciarAnalisis()

      }
      if (respuesta.ok && cuerpo?.ok && cuerpo.usuario) {
        setUsuario(cuerpo.usuario)
        setClave('')
        setSesion('activa')
        return
      }
      // Ante 401 el backend responde siempre el mensaje genérico (RF-00.3):
      // se muestra tal cual, sin revelar qué campo falló.
      setErrorLogin(cuerpo?.motivo ?? 'Usuario o contraseña incorrectos.')
    } catch {
      setErrorLogin(
        'No se pudo conectar con el servidor. Verifica que el backend esté ' +
          'en ejecución y vuelve a intentarlo.',
      )
    } finally {
      setEntrando(false)
    }
  }

  async function alCerrarSesion() {
    try {
      await fetch('/logout', { method: 'POST' })
    } finally {
      setArchivo(null)
      setResultado(null)
      setClasificacion(null)
      setTipoSeleccionado(null)
      setConfirmado(false)
      setMensajeError(null)
      setAvisoArchivo(null)
      setEstado('inicio')
      setNombre('')
      volverALogin()
    }
  }

  function alElegirArchivo(event: React.ChangeEvent<HTMLInputElement>) {
    const elegido = event.target.files?.[0] ?? null
    setResultado(null)
    setClasificacion(null)
    setTipoSeleccionado(null)
    setConfirmado(false)
    setMensajeError(null)
    setAvisoArchivo(null)

    if (!elegido) {
      setArchivo(null)
      return
    }

    const extension = extensionDe(elegido.name)
    if (!EXTENSIONES_ACEPTADAS.includes(extension)) {
      setArchivo(null)
      event.target.value = ''
      setAvisoArchivo(
        `El formato "${extension || 'sin extensión'}" no está soportado. ` +
          'Formatos aceptados: PDF y DOCX.',
      )
      return
    }

    setArchivo(elegido)
  }


  async function alEnviar(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!archivo || estado === 'cargando') return

    setEstado('cargando')
    setResultado(null)
    setClasificacion(null)
    setTipoSeleccionado(null)
    setConfirmado(false)
    setMensajeError(null)

    const datos = new FormData()
    datos.append('archivo', archivo)

    try {
      const respuesta = await fetch('/extraer', { method: 'POST', body: datos })
      if (respuesta.status === 401) {
        // La sesión caducó o se invalidó: se vuelve al login.
        volverALogin()
        return
      }
      let cuerpo: RespuestaExtraccion | null = null
      try {
        cuerpo = (await respuesta.json()) as RespuestaExtraccion
      } catch {
        cuerpo = null
      }

      if (!cuerpo) {
        setEstado('error')
        setMensajeError(
          'El servidor no devolvió una respuesta válida. Inténtalo de nuevo.',
        )
        return
      }

      if (respuesta.ok && cuerpo.ok && cuerpo.texto) {
        setResultado(cuerpo)
        setEstado('exito')
        void clasificarTexto(cuerpo.texto)
        return
      }

      setEstado('error')
      setMensajeError(
        cuerpo.motivo ??
          'No se pudo extraer el texto del documento. Inténtalo con otro archivo.',
      )
    } catch {
      setEstado('error')
      setMensajeError(
        'No se pudo conectar con el servidor. Verifica que el backend esté ' +
          'en ejecución y vuelve a intentarlo.',
      )
    }
  }


  function alConfirmarTipo() {
    if (!tipoSeleccionado) return
    setConfirmado(true)
  }

  async function clasificarTexto(texto: string) {
    setClasificando(true)
    try {
      const respuesta = await fetch('/clasificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto }),
      })
      if (respuesta.status === 401) {
        // La sesión caducó o se invalidó: se vuelve al login.
        volverALogin()
        return
      }
      let cuerpo: RespuestaClasificacion | null = null
      try {
        cuerpo = (await respuesta.json()) as RespuestaClasificacion
      } catch {
        cuerpo = null
      }
      if (!cuerpo) {
        setMensajeError(
          'El servidor no devolvió una respuesta válida al clasificar. ' +
            'Inténtalo de nuevo.',
        )
        return
      }
      if (respuesta.ok && cuerpo.ok) {
        setClasificacion(cuerpo)
        setTipoSeleccionado(cuerpo.tipo as TipoOpcion | null)
      } else {
        setMensajeError(
          cuerpo.motivo ?? 'No se pudo clasificar el tipo de contrato.',
        )
      }
    } catch {
      setMensajeError(
        'No se pudo conectar con el servidor para clasificar el contrato.',
      )
    } finally {
      setClasificando(false)
    }
  }

  if (sesion === 'consultando') {
    return (
      <main className="contenedor">
        <section className="tarjeta" aria-live="polite">

          <p>Comprobando la sesión…</p>
        </section>
      </main>
    )
  }

  if (sesion === 'sin-sesion') {
    return (
      <main className="contenedor">
        <header className="cabecera">
          <h1>MotorRevisionLegal</h1>
          <p className="descripcion">
            Revisión de cláusulas contractuales. Inicia sesión con tu cuenta
            autorizada para continuar.
          </p>
        </header>

        <section className="tarjeta">
          <form onSubmit={alIniciarSesion}>
            <label className="etiqueta" htmlFor="usuario">
              Usuario
            </label>
            <input
              id="usuario"
              name="usuario"
              type="text"
              autoComplete="username"
              value={nombre}
              onChange={(event) => setNombre(event.target.value)}
              disabled={entrando}
              required
            />

            <label className="etiqueta" htmlFor="contrasena">
              Contraseña
            </label>
            <input
              id="contrasena"
              name="contrasena"
              type="password"
              autoComplete="current-password"
              value={clave}
              onChange={(event) => setClave(event.target.value)}
              disabled={entrando}
              required
            />

            <button type="submit" disabled={entrando}>
              {entrando ? 'Iniciando sesión…' : 'Iniciar sesión'}
            </button>
          </form>

          {errorLogin && (
            <p className="aviso" role="alert">
              {errorLogin}
            </p>
          )}
        </section>

        <footer className="pie">
          <p>
            Acceso privado: solo cuentas autorizadas. Si necesitas acceso,
            contacta con quien administre el sistema.
          </p>
        </footer>
      </main>
    )
  }

  return (
    <main className="contenedor">
      <div className="barra-superior">
        <nav className="navegacion" aria-label="Navegación principal">
          <ul>
            {VISTAS.map((opcion) => (
              <li key={opcion.id}>
                <button
                  type="button"
                  onClick={() => setVista(opcion.id)}
                  aria-current={vista === opcion.id ? 'page' : undefined}
                >
                  {opcion.etiqueta}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        <div className="acciones-sesion">
          <span>
            Sesión iniciada como <strong>{usuario}</strong>
          </span>
          <button
            type="button"
            onClick={cambiarTema}
            aria-label={
              tema === 'claro'
                ? 'Cambiar a tema oscuro'
                : 'Cambiar a tema claro'
            }
          >
            {tema === 'claro' ? 'Tema oscuro' : 'Tema claro'}
          </button>
          <button type="button" onClick={() => void alCerrarSesion()}>
            Cerrar sesión
          </button>
        </div>
      </div>

      <header className="cabecera">
        <h1>MotorRevisionLegal</h1>
      </header>

      {vista === 'inicio' && (
        <section className="tarjeta" aria-live="polite">
          <h2>Bienvenido</h2>
          <p>
            Revisión de cláusulas contractuales. Para empezar, abre{' '}
            <strong>Analizar contrato</strong> y carga un contrato en PDF con
            texto seleccionable o en DOCX para extraer su texto.
          </p>
          <p className="sugerencia">
            Las secciones de Resultados e Historial estarán disponibles cuando
            el análisis y el historial estén implementados.
          </p>
        </section>
      )}

      {vista === 'analizar' && (
        <>
          <p className="descripcion">
            Carga un contrato en PDF con texto seleccionable o en DOCX para
            extraer su texto.
          </p>
          <section className="tarjeta">
        <form onSubmit={alEnviar}>
          <label className="etiqueta" htmlFor="archivo">
            Archivo del contrato
          </label>
          <input
            id="archivo"
            name="archivo"
            type="file"
            accept=".pdf,.docx"
            onChange={alElegirArchivo}
            disabled={estado === 'cargando'}
          />

          {avisoArchivo && <p className="aviso">{avisoArchivo}</p>}

          {archivo && (
            <p className="detalle-archivo">
              <strong>Archivo seleccionado:</strong> {archivo.name} ·{' '}
              {tamanoLegible(archivo.size)}
            </p>
          )}

          <button type="submit" disabled={!archivo || estado === 'cargando'}>
            {estado === 'cargando' ? 'Extrayendo texto…' : 'Extraer texto'}
          </button>
        </form>
      </section>

      {vista === 'analizar' && estado === 'cargando' && (
        <section className="tarjeta" aria-live="polite">
          <p>Extrayendo el texto del documento. Esto puede tardar unos segundos…</p>
        </section>
      )}

      {vista === 'analizar' && estado === 'error' && (
        <section className="tarjeta error" role="alert">
          <h2>No se pudo extraer el texto</h2>
          <p>{mensajeError}</p>
          <p className="sugerencia">
            Si el archivo es un PDF, comprueba que tenga texto seleccionable y no
            sea una imagen escaneada.
          </p>
        </section>
      )}

      {vista === 'analizar' && estado === 'exito' && resultado && (
        <>
          <section className="tarjeta resultado" aria-live="polite">
            <h2>Texto extraído</h2>
            <p className="metadatos">
              Formato: <strong>{resultado.formato?.toUpperCase()}</strong>
              {typeof resultado.num_paginas === 'number' && (
                <>
                  {' · '}
                  Páginas: <strong>{resultado.num_paginas}</strong>
                </>
              )}
            </p>
            <pre className="texto-extraido">{resultado.texto}</pre>
          </section>

          {!confirmado && (
            <section className="tarjeta clasificacion" aria-live="polite">
              <h2>Tipo de contrato (propuesta)</h2>

              {clasificando && !clasificacion && (
                <p>Clasificando el tipo de contrato…</p>
              )}

              {!clasificando && !clasificacion && (
                <p className="aviso">
                  {mensajeError ??
                    'No se pudo obtener la propuesta de clasificación. ' +
                      'Seleccione el tipo de contrato manualmente para continuar.'}
                </p>
              )}

              {clasificacion && (
                <>
                  <p>
                    <strong>Confianza:</strong>{' '}
                    <span
                      className={
                        clasificacion.confianza === 'alta'
                          ? 'confianza confianza-alta'
                          : 'confianza confianza-baja'
                      }
                    >
                      {clasificacion.confianza === 'alta' ? 'Alta' : 'Baja'}
                    </span>
                  </p>
                  {clasificacion.confianza === 'alta' ? (
                    <>
                      <p>
                        Clasificación local y determinista, sin IA ni envío de
                        texto a terceros.
                      </p>
                      <p className="nota-rf04">
                        RF-04: análisis de cláusulas con IA local. Los hallazgos y el informe de cláusulas se generan tras el análisis y requieren revisión humana.
                      </p>
                    </>
                  ) : (
                    <p className="aviso">
                      Atención: las señales textuales son débiles o ambiguas.
                      Revise y confirme el tipo manualmente.
                    </p>
                  )}
                  {clasificacion.etiqueta ? (
                    <p>
                      <strong>Propuesta:</strong> {clasificacion.etiqueta}
                    </p>
                  ) : (
                    <p>
                      <strong>Propuesta:</strong> no se pudo determinar
                      automáticamente.
                    </p>
                  )}
                  {clasificacion.evidencias &&
                    clasificacion.evidencias.length > 0 && (
                      <>
                        <p><strong>Evidencias en el texto:</strong></p>
                        <ul>
                          {deduplicarEvidencias(
                            resultado.texto,
                            clasificacion.evidencias,
                          ).map((evidencia, i) => (
                            <li key={i}>{evidencia}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  {clasificacion.motivo && (
                    <p className="aviso">{clasificacion.motivo}</p>
                  )}
                </>
              )}
              <fieldset>
                <legend>Seleccionar tipo de contrato</legend>
                {OPCIONES_TIPO.map((opcion) => (
                  <label key={opcion.id}>
                    <input
                      type="radio"
                      name="tipo-contrato"
                      value={opcion.id}
                      checked={tipoSeleccionado === opcion.id}
                      onChange={() => setTipoSeleccionado(opcion.id)}
                      disabled={clasificando}
                    />
                    {opcion.etiqueta}
                  </label>
                ))}
              </fieldset>
              <button
                type="button"
                disabled={!tipoSeleccionado || clasificando}
                onClick={alConfirmarTipo}
              >


                {clasificando ? 'Confirmando…' : 'Confirmar tipo de contrato'}
              </button>
              <p className="sugerencia">
                Puede corregir la propuesta eligiendo el otro tipo antes de
                confirmar.
              </p>
            </section>
          )}
          {confirmado && tipoSeleccionado && (
            <section className="tarjeta analisis" aria-live="polite">
              <h2>Análisis de cláusulas (prototipo local)</h2>
              <p className="sugerencia">
                El análisis usa IA local en este equipo. Puede tardar varios
                minutos. No cierre esta vista mientras se procesa.
              </p>
              <button
                type="button"
                disabled={
                  analizando || servidorOcupado || !resultado?.texto
                }
                onClick={alAnalizarClausulas}
              >
                {analizando
                  ? 'Analizando…'
                  : 'Analizar cláusulas con IA local'}
              </button>
              {analizando && (
                <>
                  <p aria-live="polite">
                    Analizando localmente, puede tardar varios minutos. No
                    cierre esta vista.
                  </p>
                  <button type="button" onClick={alDejarDeEsperar}>
                    Dejar de esperar
                  </button>
                </>
              )}
              {servidorOcupado && !analizando && (
                <p className="aviso">
                  El servidor local está ocupado o su estado no pudo
                  verificarse. Reintente solo cuando esté libre.
                </p>
              )}
              {errorAnalisis && (
                <p className="aviso" role="alert">
                  {errorAnalisis}
                </p>
              )}
              {hallazgos && (
                <>
                  {hallazgos.length === 0 ? (
                    <p>
                      No se identificaron hallazgos con los criterios
                      aplicados. Esto no garantiza que el contrato esté libre
                      de problemas.
                    </p>
                  ) : (
                    <>
                      {Object.values(
                        hallazgos.reduce(
                          (acc, hallazgo) => {
                            (acc[hallazgo.categoria] =
                              acc[hallazgo.categoria] || []).push(hallazgo);
                            return acc;
                          },
                          {} as Record<string, HallazgoAnalisis[]>
                        )
                      )
                        .filter((grupo) => grupo.length > 0)
                        .map((grupo, gi) => (
                          <section
                            key={grupo[0]?.categoria ?? String(gi)}
                          >
                            <h3>{grupo[0]?.categoria ?? 'Sin categoría'}</h3>
                            <ol className="lista-hallazgos">
                              {grupo.map((hallazgo, i) => (
                                <Hallazgo key={i} hallazgo={hallazgo} />
                              ))}
                            </ol>
                          </section>
                        ))}
                    </>
                      )}
                  {numDescartados > 0 && (
                    <p className="sugerencia">
                      {numDescartados === 1
                        ? 'Se descartó 1 cita que no existía literalmente en '
                          + 'el texto.'
                        : `Se descartaron ${numDescartados} citas que no `
                          + 'existían literalmente en el texto.'}
                    </p>
                  )}
                  <p className="aviso">
                    Este informe es generado automáticamente y no constituye
                    asesoría jurídica. Los resultados deben ser revisados por
                    una persona con formación jurídica antes de tomar
                    decisiones. El sistema no afirma que un contrato sea
                    válido, legal ni que cumpla con la ley.
                  </p>
                </>
              )}
            </section>
          )}

          {confirmado && tipoSeleccionado && (
            <section className="tarjeta" aria-live="polite">
              <h2>Tipo confirmado</h2>
              <p>
                El tipo seleccionado es{' '}
                <strong>{etiquetaDe(tipoSeleccionado)}</strong>.
              </p>
            </section>
          )}
        </>
      )}
        </>
      )}

      {vista === 'resultados' && (
        <section className="tarjeta" aria-live="polite">
          <h2>Resultados</h2>
          <p>
            No hay resultados para mostrar todavía. Analiza un contrato en Analizar contrato para que aparezca aquí.
          </p>
          <p className="sugerencia">
            Mientras tanto, puedes extraer el texto de un contrato en{' '}
            <strong>Analizar contrato</strong>.
          </p>
        </section>
      )}

      {vista === 'historial' && (
        <section className="tarjeta" aria-live="polite">
          <h2>Historial</h2>
          {cargandoHistorial && (
            <p>Cargando tu historial de análisis…</p>
          )}
          {errorHistorial && (
            <p className="aviso" role="alert">{errorHistorial}</p>
          )}
          {!cargandoHistorial && !errorHistorial && historial !== null && (
            <>
              {historial.length === 0 ? (
                <p>
                  No hay análisis registrados todavía. Analiza un contrato en{' '}
                  <strong>Analizar contrato</strong> para que aparezca aquí.
                </p>
              ) : (
                <ul>
                  {historial.map((registro) => (
                    <li key={registro.id}>
                      <p>
                        <strong>{formatearFechaLocal(registro.fecha)}</strong> —{' '}
                        {registro.tipo_confirmado}{' '}
                        ({registro.num_hallazgos} hallazgo{
                          registro.num_hallazgos !== 1 ? 'es' : ''
                        })
                      </p>
                      {registro.hallazgos?.length ? (
                        <ol className="lista-hallazgos">
                          {(registro.hallazgos ?? []).map((hallazgo, i) => (
                            <Hallazgo key={i} hallazgo={hallazgo} />
                          ))}
                        </ol>
                       ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </section>
      )}

      <footer className="pie">
        <p>
          Esta herramienta apoya la revisión contractual. Los resultados deben
          ser revisados por una persona con formación jurídica.
        </p>
      </footer>
    </main>
  )
}
