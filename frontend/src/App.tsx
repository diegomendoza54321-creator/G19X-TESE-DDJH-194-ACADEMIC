/**
 * Interfaz del MVP: inicio de sesión y extracción de texto de PDF o DOCX.
 *
 * Cubre RF-00 (autenticación privada), RF-01 (carga), RF-02 (extracción) y
 * RF-06 (interfaz en español). No incluye IA: solo extrae el texto.
 *
 * Autenticación: al abrir se consulta GET /yo; solo con sesión válida se
 * muestra la pantalla de carga. El login usa los campos del backend
 * (usuario, contrasena) y la sesión viaja en cookie HttpOnly: el navegador
 * nunca guarda contraseñas ni tokens. Sin registro público (RF-00.2).
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

type Sesion = 'consultando' | 'sin-sesion' | 'activa'
type Estado = 'inicio' | 'cargando' | 'exito' | 'error'

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

  const [archivo, setArchivo] = useState<File | null>(null)
  const [avisoArchivo, setAvisoArchivo] = useState<string | null>(null)
  const [estado, setEstado] = useState<Estado>('inicio')
  const [resultado, setResultado] = useState<RespuestaExtraccion | null>(null)
  const [mensajeError, setMensajeError] = useState<string | null>(null)

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
      <header className="cabecera">
        <h1>MotorRevisionLegal</h1>
        <p className="descripcion">
          Revisión de cláusulas contractuales. Carga un contrato en PDF con
          texto seleccionable o en DOCX para extraer su texto.
        </p>
        <p className="detalle-archivo">
          Sesión iniciada como <strong>{usuario}</strong>
          {' · '}
          <button type="button" onClick={() => void alCerrarSesion()}>
            Cerrar sesión
          </button>
        </p>
      </header>

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

      {estado === 'cargando' && (
        <section className="tarjeta" aria-live="polite">
          <p>Extrayendo el texto del documento. Esto puede tardar unos segundos…</p>
        </section>
      )}

      {estado === 'error' && (
        <section className="tarjeta error" role="alert">
          <h2>No se pudo extraer el texto</h2>
          <p>{mensajeError}</p>
          <p className="sugerencia">
            Si el archivo es un PDF, comprueba que tenga texto seleccionable y no
            sea una imagen escaneada.
          </p>
        </section>
      )}

      {estado === 'exito' && resultado && (
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
