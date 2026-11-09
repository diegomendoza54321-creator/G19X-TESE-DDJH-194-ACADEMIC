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
        <h1>Bienvenido, {usuario}</h1>
        <p className="dashboard-subtitulo">
          Revisión de cláusulas contractuales con IA local
        </p>
      </header>

      <div className="metricas-grid">
        <div className="metrica-tarjeta">
          <div className="metrica-valor">{contratosAnalizados}</div>
          <div className="metrica-label">Contratos analizados</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-valor">{hallazgosDetectados}</div>
          <div className="metrica-label">Hallazgos detectados</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-valor">Phi-3 Mini</div>
          <div className="metrica-label">IA local</div>
        </div>
        <div className="metrica-tarjeta">
          <div className="metrica-valor">{usuario ?? '—'}</div>
          <div className="metrica-label">Usuario actual</div>
        </div>
      </div>

      <div className="acciones-rapidas">
        <h2 className="acciones-titulo">Acciones rápidas</h2>
        <div className="acciones-botones">
          <button type="button" onClick={onAnalizar} className="btn-primario">
            Analizar contrato
          </button>
          <button type="button" onClick={onHistorial} className="btn-secundario">
            Ver historial
          </button>
        </div>
      </div>
    </section>
  )
}
