import SidebarLateral from './SidebarLateral'

interface LayoutPrincipalProps {
  children: React.ReactNode
  vista: string
  setVista: (id: string) => void
  tema: string
  setTema: (t: string) => void
  usuario: string | null
  onLogout: () => void
}

export default function LayoutPrincipal({
  children,
  vista,
  setVista,
  tema,
  setTema,
  usuario,
  onLogout,
}: LayoutPrincipalProps) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <SidebarLateral
          vista={vista}
          setVista={setVista}
          tema={tema}
          setTema={setTema}
          usuario={usuario}
          onLogout={onLogout}
        />
      </aside>
      <main className="contenido-principal">{children}</main>
    </div>
  )
}
