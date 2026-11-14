interface TarjetaResultadoProps {
  hallazgo: any
}

const TIPO_LABEL: Record<string, string> = {
  ambiguedad: 'Ambigüedad',
  omision: 'Omisión',
  contradiccion: 'Contradicción',
  riesgo: 'Riesgo',
}

export default function TarjetaResultado({ hallazgo }: TarjetaResultadoProps) {
  const tipo = hallazgo.tipo
  const tipoLabel = TIPO_LABEL[tipo] || tipo
  const tieneCita = hallazgo.cita && hallazgo.cita.trim().length > 0

  return (
    <article className="tarjeta-resultado">
      <div className="tarjeta-resultado-header">
        <span className={`badge badge-${tipo}`}>
          {tipoLabel}
        </span>
        <span className="badge categoria">
          {hallazgo.categoria}
        </span>
      </div>
      <div className="tarjeta-resultado-contenido">
        <p className="tarjeta-resultado-descripcion">{hallazgo.descripcion}</p>
        {tieneCita && (
          <blockquote className="tarjeta-resultado-cita">
            <span className="marca-cita" aria-hidden="true">“</span>
            {hallazgo.cita}
            <span className="marca-cita-final" aria-hidden="true">”</span>
          </blockquote>
        )}
        <div className="detalles-grid">
          <div className="detalle">
            <span className="etiqueta-detalle">Explicación</span>
            <span className="valor-detalle">{hallazgo.explicacion}</span>
          </div>
          <div className="detalle">
            <span className="etiqueta-detalle">Consecuencia</span>
            <span className="valor-detalle">{hallazgo.consecuencia}</span>
          </div>
          <div className="detalle">
            <span className="etiqueta-detalle">Recomendación</span>
            <span className="valor-detalle">{hallazgo.recomendacion}</span>
          </div>
          <div className="detalle">
            <span className="etiqueta-detalle">Limitaciones</span>
            <span className="valor-detalle">{hallazgo.limitaciones}</span>
          </div>
        </div>
      </div>
    </article>
  )
}
