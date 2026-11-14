const ICONO_CONTRATOS = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
  </svg>
`
const ICONO_HALLAZGOS = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="8" x2="12" y2="16"></line>
    <line x1="8" y1="12" x2="16" y2="12"></line>
  </svg>
`
const ICONO_IA = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
    <path d="M2 17l10 5 10-5"></path>
    <path d="M2 12l10 5 10-5"></path>
  </svg>
`
const ICONO_USUARIO = `
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
`

interface RegistroHistorial {
  id: number
  fecha: string
  tipo_confirmado: string
  num_hallazgos: number
  hallazgos: any[]
}

interface DashboardInicioProps {
  usuario: string | null
  historial: RegistroHistorial[] | null
  onAnalizar: () => void
  onHistorial: () => void
}

export default function DashboardInicio({
  usuario,
  historial,
  onAnalizar,
  onHistorial,
}: DashboardInicioProps) {
  const contratosAnalizados = historial ? historial.length : 0
  const hallazgosDetectados = historial
    ? historial.reduce((acc, registro) => acc + (registro.num_hallazgos || 0), 0)
    : 0

  return (
    <section className="dashboard">
      <header className="dashboard-header">
        <div className="bienvenida">
          <h1>Bienvenido, {usuario}</h1>
          <p className="dashboard-subtitulo">
            Revisión de cláusulas contractuales con IA local
          </p>
        </div>
      </header>

      <div className="metricas-grid">
        <div className="metrica-tarjeta">
          <div className="metrica-icono" dangerouslySetInnerHTML={{ __html: ICONO_CONTRATOS }} />
          <div className="metrica-valor">{contratosAnalizados}</div>
          <div className="metrica-label">Contratos analizados</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-icono" dangerouslySetInnerHTML={{ __html: ICONO_HALLAZGOS }} />
          <div className="metrica-valor">{hallazgosDetectados}</div>
          <div className="metrica-label">Hallazgos detectados</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-icono" dangerouslySetInnerHTML={{ __html: ICONO_IA }} />
          <div className="metrica-valor">Phi-3 Mini</div>
          <div className="metrica-label">IA local</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-icono" dangerouslySetInnerHTML={{ __html: ICONO_USUARIO }} />
          <div className="metrica-valor">{usuario ?? '—'}</div>
          <div className="metrica-label">Usuario actual</div>
        </div>
      </div>

      <div className="acciones-rapidas">
        <h2 className="acciones-titulo">Acciones rápidas</h2>
        <div className="acciones-botones">
          <button type="button" onClick={onAnalizar} className="btn-primario-moderno btn-pequeno-moderno">
            <span className="icono-accion" aria-hidden="true">📄</span>
            Analizar contrato
          </button>
          <button type="button" onClick={onHistorial} className="btn-secundario-moderno btn-pequeno-moderno">
            <span className="icono-accion" aria-hidden="true">📋</span>
            Ver historial
          </button>
        </div>
      </div>
    </section>
  )
}
