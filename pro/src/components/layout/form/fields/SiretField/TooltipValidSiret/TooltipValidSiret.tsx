import Icon from 'components/layout/Icon'
import React from 'react'

const TooltipValidSiret = (): JSX.Element => {
  return (
    <span
      className="button"
      data-place="bottom"
      data-tip="<p>Il n’est pas possible de modifier le nom, l’addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
      data-type="info"
    >
      <Icon svg="picto-info" />
    </span>
  )
}

export default TooltipValidSiret
