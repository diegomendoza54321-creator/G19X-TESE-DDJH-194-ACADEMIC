/**
 * Pantalla inicial del MVP: carga de un contrato en PDF o DOCX y extracción
 * de su texto.
 *
 * Cubre temporalmente RF-01 (carga), RF-02 (extracción) y RF-06 (interfaz en
 * español) hasta que exista la navegación completa (RF-07). No incluye IA:
 * este bloque solo extrae el texto y lo muestra.
 *
 * La llamada se hace a rutas relativas; el dev server de Vite las redirige al
 * backend FastAPI (ver vite.config.ts), así que no hace falta configurar CORS.
 */

import { useState } from 'react'
import './App.css'

/** Formatos aceptados por el backend, según RF-01.1 y RF-01.2. */
const EXTENSIONES_ACEPTADAS = ['.pdf', '.docx']

interface RespuestaExtraccion {
  ok: boolean
  texto: string | null
  formato: string | null
  num_paginas: number | null
  codigo: string | null
  motivo: string | null
}

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
  const [archivo, setArchivo] = useState<File | null>(null)
  const [avisoArchivo, setAvisoArchivo] = useState<string | null>(null)
  const [estado, setEstado] = useState<Estado>('inicio')
  const [resultado, setResultado] = useState<RespuestaExtraccion | null>(null)
  const [mensajeError, setMensajeError] = useState<string | null>(null)

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

  return (
    <main className="contenedor">
      <header className="cabecera">
        <h1>MotorRevisionLegal</h1>
        <p className="descripcion">
          Revisión de cláusulas contractuales. Carga un contrato en PDF con
          texto seleccionable o en DOCX para extraer su texto.
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
