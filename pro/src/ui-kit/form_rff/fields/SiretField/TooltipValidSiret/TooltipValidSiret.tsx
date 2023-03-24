import React from 'react'

import Icon from 'ui-kit/Icon/Icon'

const TooltipValidSiret = (): JSX.Element => {
  return (
    <span
      className="button react-tooltip-anchor"
      data-tooltip-place="bottom"
      data-tooltip-html="<p>Il n’est pas possible de modifier le nom, l’addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
      data-tooltip-type="info"
    >
      <Icon svg="picto-info" />
    </span>
  )
}

export default TooltipValidSiret
