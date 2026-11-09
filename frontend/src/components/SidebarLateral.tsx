const VISTAS: { id: string; etiqueta: string }[] = [
  { id: 'inicio', etiqueta: 'Inicio' },
  { id: 'analizar', etiqueta: 'Analizar contrato' },
  { id: 'resultados', etiqueta: 'Resultados' },
  { id: 'historial', etiqueta: 'Historial' },
]

interface SidebarLateralProps {
  vista: string
  setVista: (id: string) => void
  tema: string
  setTema: (t: string) => void
  usuario: string | null
  onLogout: () => void
}

export default function SidebarLateral({
  vista,
  setVista,
  tema,
  setTema,
  usuario,
  onLogout,
}: SidebarLateralProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>MotorRevisionLegal</h2>
      </div>
      <nav className="sidebar-nav" aria-label="Navegación principal">
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
      <div className="sidebar-sesion">
        <p className="usuario-actual">
          Sesión iniciada como <strong>{usuario}</strong>
        </p>
        <button
          type="button"
          onClick={() => setTema(tema === 'claro' ? 'oscuro' : 'claro')}
          aria-label={
            tema === 'claro'
              ? 'Cambiar a tema oscuro'
              : 'Cambiar a tema claro'
          }
        >
          {tema === 'claro' ? 'Tema oscuro' : 'Tema claro'}
        </button>
        <button type="button" onClick={onLogout}>
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
