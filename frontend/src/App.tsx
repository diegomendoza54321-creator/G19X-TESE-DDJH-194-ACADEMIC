/**
 * Interfaz del MVP: inicio de sesión, navegación, tema y extracción.
 *
 * Cubre RF-00 (autenticación privada), RF-01 (carga), RF-02 (extracción),
 * RF-06 (interfaz en español) y RF-07 (navegación principal y tema claro /
 * oscuro). No incluye IA: este bloque solo extrae el texto y lo muestra.
 *
 * Navegación (RF-07.1): tras iniciar sesión hay cuatro secciones, Inicio,
 * Analizar contrato, Resultados e Historial. La carga y extracción viven en
 * Analizar contrato. Resultados e Historial muestran estados vacíos honestos
 * mientras esas funciones no existan: no se inventa ningún análisis.
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

import { useEffect, useState } from 'react'
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
  const [clasificando, setClasificando] = useState(false)

  // Al abrir, la sesión vive en la cookie HttpOnly: se consulta al backend.
  useEffect(() => {
    let activa = true
    async function consultarSesion() {
      try {
        const respuesta = await fetch('/yo')
        let cuerpo: RespuestaSesion | null = null
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
                Evidencias: eliminar duplicados exactos y fragmentos que estén
              <p><strong>Confianza:</strong> {clasificacion?.confianza === 'alta' ? 'alta' : 'baja'}</p>
              {clasificacion?.confianza === 'alta' ? (
                <p>
                  Clasificación local y determinista, sin IA ni envío de texto
                  a terceros.
                </p>
              ) : (
                <p className="aviso">
                  Atención: las señales textuales son débiles o ambiguas.
                  Revise y confirme el tipo manualmente.
                </p>
              )}
              {clasificacion?.etiqueta ? (
                <p>
                  <strong>Propuesta:</strong> {clasificacion.etiqueta}
                </p>
              ) : (
                <p>
                  <strong>Propuesta:</strong> no se pudo determinar
                  automáticamente.
                </p>
              )}
              {clasificacion?.evidencias && clasificacion.evidencias.length > 0 && (
                <>
                  <p><strong>Evidencias en el texto:</strong></p>
                  <ul>
                    {clasificacion.evidencias
                      .filter((e, i, arr) => arr.indexOf(e) === i)
                      .filter((e, i, arr) => !arr.some((o, j) => j !== i && o !== e && o.includes(e)))
                      .map((evidencia, i) => (
                        <li key={i}>{evidencia}</li>
                      ))}
                  </ul>
                </>
              )}
              {clasificacion?.motivo && (
                <p className="aviso">{clasificacion.motivo}</p>
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
            <section className="tarjeta" aria-live="polite">
              <h2>Tipo confirmado</h2>
              <p>
                El tipo seleccionado es{' '}
                <strong>{etiquetaDe(tipoSeleccionado)}</strong>.
              </p>
              <p className="aviso">
                El análisis de cláusulas (hallazgos e informe) todavía no está
                implementado: está pendiente de la selección del proveedor de
                IA para RF-04. No se generan hallazgos ni citas hasta que ese
                módulo exista.
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
            Todavía no hay resultados para mostrar. El análisis de contratos
            (clasificación, hallazgos e informe) aún no está implementado.
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
          <p>
            Todavía no hay análisis registrados. El historial estará
            disponible cuando el análisis y su registro estén implementados.
          </p>
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
