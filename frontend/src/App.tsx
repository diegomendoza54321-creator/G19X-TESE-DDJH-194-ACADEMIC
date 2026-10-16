/**
 * Interfaz del MVP: inicio de sesiÃƒÂ³n, navegaciÃƒÂ³n, tema y extracciÃƒÂ³n.
 *
 * Cubre RF-00 (autenticaciÃƒÂ³n privada), RF-01 (carga), RF-02 (extracciÃƒÂ³n),
 * RF-06 (interfaz en espaÃƒÂ±ol) y RF-07 (navegaciÃƒÂ³n principal y tema claro /
 * oscuro). No incluye IA: este bloque solo extrae el texto y lo muestra.
 *
 * NavegaciÃƒÂ³n (RF-07.1): tras iniciar sesiÃƒÂ³n hay cuatro secciones, Inicio,
 * Analizar contrato, Resultados e Historial. La carga y extracciÃƒÂ³n viven en
 * Analizar contrato. Resultados e Historial muestran estados vacÃƒÂ­os honestos
 * mientras esas funciones no existan: no se inventa ningÃƒÂºn anÃƒÂ¡lisis.
 *
 * Tema (RF-07.2 a RF-07.5): control claro/oscuro en la barra superior. La
 * preferencia se guarda en localStorage y se restaura al recargar; sin
 * preferencia se usa el tema del sistema. Cambiarlo no cierra la sesiÃƒÂ³n ni
 * borra el trabajo: solo cambia el atributo data-tema en <html>.
 *
 * AutenticaciÃƒÂ³n: al abrir se consulta GET /yo; solo con sesiÃƒÂ³n vÃƒÂ¡lida se
 * muestra la navegaciÃƒÂ³n. El login usa los campos del backend (usuario,
 * contrasena) y la sesiÃƒÂ³n viaja en cookie HttpOnly: el navegador nunca
 * guarda contraseÃƒÂ±as ni tokens. Sin registro pÃƒÂºblico (RF-00.2).
 *
 * Llamadas a rutas relativas; el dev server las redirige al backend
 * (ver vite.config.ts), asÃƒÂ­ que no hace falta CORS.
 */

import { useEffect, useState } from 'react'
import './App.css'

/** Formatos aceptados por el backend, segÃƒÂºn RF-01.1 y RF-01.2. */
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
  { id: 'prestacion_de_servicios', etiqueta: 'PrestaciÃƒÂ³n de servicios' },
  { id: 'proveedor', etiqueta: 'Contrato de proveedor' },
]

function etiquetaDe(tipo: TipoOpcion | null): string {
  if (!tipo) return ''
  const opcion = OPCIONES_TIPO.find((o) => o.id === tipo)
  return opcion ? opcion.etiqueta : ''
}

type Sesion = 'consultando' | 'sin-sesion' | 'activa'
type Estado = 'inicio' | 'cargando' | 'exito' | 'error'

/** Secciones de la navegaciÃƒÂ³n principal (RF-07.1). */
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

  // NavegaciÃƒÂ³n principal y tema (RF-07). Ambos viven en el estado de React:
  // cambiar de vista o de tema no toca la sesiÃƒÂ³n ni el trabajo en curso.
  const [vista, setVista] = useState<Vista>('inicio')
  const [tema, setTema] = useState<Tema>(leerTemaInicial)

  const [archivo, setArchivo] = useState<File | null>(null)
  const [avisoArchivo, setAvisoArchivo] = useState<string | null>(null)
  const [estado, setEstado] = useState<Estado>('inicio')
  const [resultado, setResultado] = useState<RespuestaExtraccion | null>(null)
  const [mensajeError, setMensajeError] = useState<string | null>(null)

  // ClasificaciÃƒÂ³n del tipo de contrato (RF-03): propuesta del backend local,
  // selecciÃƒÂ³n corregible por el usuario y confirmaciÃƒÂ³n explÃƒÂ­cita.
  const [clasificacion, setClasificacion] = useState<RespuestaClasificacion | null>(null)
  const [tipoSeleccionado, setTipoSeleccionado] = useState<TipoOpcion | null>(null)
  const [confirmado, setConfirmado] = useState(false)
  const [clasificando, setClasificando] = useState(false)

  // Al abrir, la sesiÃƒÂ³n vive en la cookie HttpOnly: se consulta al backend.
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
  // el atributo visual y localStorage: la sesiÃƒÂ³n y el trabajo siguen intactos.
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
      // Ante 401 el backend responde siempre el mensaje genÃƒÂ©rico (RF-00.3):
      // se muestra tal cual, sin revelar quÃƒÂ© campo fallÃƒÂ³.
      setErrorLogin(cuerpo?.motivo ?? 'Usuario o contraseÃƒÂ±a incorrectos.')
    } catch {
      setErrorLogin(
        'No se pudo conectar con el servidor. Verifica que el backend estÃƒÂ© ' +
          'en ejecuciÃƒÂ³n y vuelve a intentarlo.',
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
        `El formato "${extension || 'sin extensiÃƒÂ³n'}" no estÃƒÂ¡ soportado. ` +
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
        // La sesiÃƒÂ³n caducÃƒÂ³ o se invalidÃƒÂ³: se vuelve al login.
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
          'El servidor no devolviÃƒÂ³ una respuesta vÃƒÂ¡lida. IntÃƒÂ©ntalo de nuevo.',
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
          'No se pudo extraer el texto del documento. IntÃƒÂ©ntalo con otro archivo.',
      )
    } catch {
      setEstado('error')
      setMensajeError(
        'No se pudo conectar con el servidor. Verifica que el backend estÃƒÂ© ' +
          'en ejecuciÃƒÂ³n y vuelve a intentarlo.',
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

          <p>Comprobando la sesiÃƒÂ³nÃ¢â‚¬Â¦</p>
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
            RevisiÃƒÂ³n de clÃƒÂ¡usulas contractuales. Inicia sesiÃƒÂ³n con tu cuenta
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
              ContraseÃƒÂ±a
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
              {entrando ? 'Iniciando sesiÃƒÂ³nÃ¢â‚¬Â¦' : 'Iniciar sesiÃƒÂ³n'}
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
        <nav className="navegacion" aria-label="NavegaciÃƒÂ³n principal">
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
            SesiÃƒÂ³n iniciada como <strong>{usuario}</strong>
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
            Cerrar sesiÃƒÂ³n
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
            RevisiÃƒÂ³n de clÃƒÂ¡usulas contractuales. Para empezar, abre{' '}
            <strong>Analizar contrato</strong> y carga un contrato en PDF con
            texto seleccionable o en DOCX para extraer su texto.
          </p>
          <p className="sugerencia">
            Las secciones de Resultados e Historial estarÃƒÂ¡n disponibles cuando
            el anÃƒÂ¡lisis y el historial estÃƒÂ©n implementados.
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
              <strong>Archivo seleccionado:</strong> {archivo.name} Ã‚Â·{' '}
              {tamanoLegible(archivo.size)}
            </p>
          )}

          <button type="submit" disabled={!archivo || estado === 'cargando'}>
            {estado === 'cargando' ? 'Extrayendo textoÃ¢â‚¬Â¦' : 'Extraer texto'}
          </button>
        </form>
      </section>

      {vista === 'analizar' && estado === 'cargando' && (
        <section className="tarjeta" aria-live="polite">
          <p>Extrayendo el texto del documento. Esto puede tardar unos segundosÃ¢â‚¬Â¦</p>
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
            <h2>Texto extraÃƒÂ­do</h2>
            <p className="metadatos">
              Formato: <strong>{resultado.formato?.toUpperCase()}</strong>
              {typeof resultado.num_paginas === 'number' && (
                <>
                  {' Ã‚Â· '}
                  PÃƒÂ¡ginas: <strong>{resultado.num_paginas}</strong>
                </>
              )}
            </p>
            <pre className="texto-extraido">{resultado.texto}</pre>
          </section>

          {!confirmado && (
            <section className="tarjeta clasificacion" aria-live="polite">
              <h2>Tipo de contrato (propuesta)</h2>
              {clasificacion?.confianza === 'alta' ? (
                <p>
                  ClasificaciÃƒÂ³n local y determinista, sin IA ni envÃƒÂ­o de texto
                  a terceros.
                </p>
              ) : (
                <p className="aviso">
                  AtenciÃƒÂ³n: las seÃƒÂ±ales textuales son dÃƒÂ©biles o ambiguas.
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
                  automÃƒÂ¡ticamente.
                </p>
              )}
              {clasificacion?.evidencias && clasificacion.evidencias.length > 0 && (
                <>
                  <p><strong>Evidencias en el texto:</strong></p>
                  <ul>
                    {clasificacion.evidencias.map((evidencia, i) => (
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
                {clasificando ? 'ConfirmandoÃ¢â‚¬Â¦' : 'Confirmar tipo de contrato'}
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
                El anÃƒÂ¡lisis de clÃƒÂ¡usulas (hallazgos e informe) todavÃƒÂ­a no estÃƒÂ¡
                implementado: estÃƒÂ¡ pendiente de la selecciÃƒÂ³n del proveedor de
                IA para RF-04. No se generan hallazgos ni citas hasta que ese
                mÃƒÂ³dulo exista.
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
            TodavÃƒÂ­a no hay resultados para mostrar. El anÃƒÂ¡lisis de contratos
            (clasificaciÃƒÂ³n, hallazgos e informe) aÃƒÂºn no estÃƒÂ¡ implementado.
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
            TodavÃƒÂ­a no hay anÃƒÂ¡lisis registrados. El historial estarÃƒÂ¡
            disponible cuando el anÃƒÂ¡lisis y su registro estÃƒÂ©n implementados.
          </p>
        </section>
      )}

      <footer className="pie">
        <p>
          Esta herramienta apoya la revisiÃƒÂ³n contractual. Los resultados deben
          ser revisados por una persona con formaciÃƒÂ³n jurÃƒÂ­dica.
        </p>
      </footer>
    </main>
  )
}
