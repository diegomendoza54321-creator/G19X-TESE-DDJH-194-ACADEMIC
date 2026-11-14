const VISTAS: { id: string; etiqueta: string; icono: string }[] = [
  {
    id: 'inicio',
    etiqueta: 'Inicio',
    icono: `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
    `,
  },
  {
    id: 'analizar',
    etiqueta: 'Analizar contrato',
    icono: `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
      </svg>
    `,
  },
  {
    id: 'resultados',
    etiqueta: 'Resultados',
    icono: `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
        <polyline points="2 17 12 22 22 17"></polyline>
        <polyline points="2 12 12 17 22 12"></polyline>
      </svg>
    `,
  },
  {
    id: 'historial',
    etiqueta: 'Historial',
    icono: `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
        <path d="M3 3v5h5a10 10 0 0 1 9 11m0 0H3m9 11v-6"></path>
      </svg>
    `,
  },
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
  const iconoBalance = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <line x1="18" y1="20" x2="6" y2="20"></line>
      <path d="M12 4v11M4 20h16m-4-8v7m-4-7v8m-8 0V8m12 4v8"></path>
    </svg>
  `

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="icono-balanza" aria-hidden="true" dangerouslySetInnerHTML={{ __html: iconoBalance }} />
          <span className="nombre-app">MotorRevisionLegal</span>
        </div>
      </div>
      <nav className="sidebar-nav" aria-label="Navegación principal">
        <ul>
          {VISTAS.map((opcion) => (
            <li key={opcion.id}>
              <button
                type="button"
                onClick={() => setVista(opcion.id)}
                aria-current={vista === opcion.id ? 'page' : undefined}
                className={
                  vista === opcion.id
                    ? 'nav-item activo'
                    : 'nav-item'
                }
              >
                <span className="icono" aria-hidden="true" dangerouslySetInnerHTML={{ __html: opcion.icono }} />
                <span className="etiqueta">{opcion.etiqueta}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
      <div className="sidebar-sesion">
        <p className="usuario-actual">
          <span className="icono-usuario" aria-hidden="true">{usuario}</span>
        </p>
        <button
          type="button"
          onClick={() => setTema(tema === 'claro' ? 'oscuro' : 'claro')}
          aria-label={
            tema === 'claro'
              ? 'Cambiar a tema oscuro'
              : 'Cambiar a tema claro'
          }
          className="btn-tema"
        >
          <span className="icono-tema" aria-hidden="true">
            {tema === 'claro' ? '🌙' : '☀️'}
          </span>
          {tema === 'claro' ? 'Tema oscuro' : 'Tema claro'}
        </button>
        <button type="button" onClick={onLogout} className="btn-salir">
          <span className="icono-salir" aria-hidden="true">🚪</span>
          Cerrar sesión
        </button>
      </div>
    </aside>
  )
}
