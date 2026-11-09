interface TarjetaResultadoProps {
  hallazgo: any
}

const COLORES_POR_TIPO: Record<string, { fondo: string; borde: string; texto: string }> = {
  ambiguedad: {
    fondo: 'var(--color-aviso-fondo)',
    borde: 'var(--color-aviso)',
    texto: 'var(--color-aviso)',
  },
  omision: {
    fondo: 'var(--color-info-fondo)',
    borde: 'var(--color-info)',
    texto: 'var(--color-info)',
  },
  contradiccion: {
    fondo: 'var(--color-error-fondo)',
    borde: 'var(--color-error)',
    texto: 'var(--color-error)',
  },
  riesgo: {
    fondo: 'var(--color-riesgo-fondo)',
    borde: 'var(--color-riesgo)',
    texto: 'var(--color-riesgo)',
  },
}

function obtenerColores(tipo: string) {
  return COLORES_POR_TIPO[tipo] ?? {
    fondo: 'var(--color-fondo-bloque)',
    borde: 'var(--color-borde)',
    texto: 'var(--color-texto)',
  }
}

export default function TarjetaResultado({ hallazgo }: TarjetaResultadoProps) {
  const colores = obtenerColores(hallazgo.tipo)

  return (
    <article
      className="tarjeta-resultado"
      style={{
        backgroundColor: colores.fondo,
        borderColor: colores.borde,
      }}
    >
      <div className="tarjeta-resultado-header">
        <span className="tarjeta-resultado-tipo" style={{ color: colores.texto }}>
          {hallazgo.tipo.charAt(0).toUpperCase() + hallazgo.tipo.slice(1)}
        </span>
        <span className="tarjeta-resultado-categoria">{hallazgo.categoria}</span>
      </div>
      <div className="tarjeta-resultado-contenido">
        <p className="tarjeta-resultado-descripcion">{hallazgo.descripcion}</p>
        {hallazgo.cita && (
          <blockquote className="tarjeta-resultado-cita">“{hallazgo.cita}”</blockquote>
        )}
        <p className="tarjeta-resultado-explicacion">
          <strong>Explicación:</strong> {hallazgo.explicacion}
        </p>
        <p className="tarjeta-resultado-consecuencia">
          <strong>Posible consecuencia:</strong> {hallazgo.consecuencia}
        </p>
        <p className="tarjeta-resultado-recomendacion">
          <strong>Recomendación:</strong> {hallazgo.recomendacion}
        </p>
        <p className="tarjeta-resultado-limitaciones">
          <strong>Limitaciones:</strong> {hallazgo.limitaciones}
        </p>
      </div>
    </article>
  )
}
