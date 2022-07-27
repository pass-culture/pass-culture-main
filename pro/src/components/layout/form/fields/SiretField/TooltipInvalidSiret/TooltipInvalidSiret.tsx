import React from 'react'

import Icon from 'components/layout/Icon'

const TooltipInvalidSiret = (): JSX.Element => {
  return (
    <span
      className="button"
      data-place="bottom"
      data-tip="<div><p>Saisissez ici le SIRET du lieu lié à votre structure pour retrouver ses informations automatiquement.</p>
      <p>Si les informations ne correspondent pas au SIRET saisi, <a href='mailto:support-pro@passculture.app?subject=Question%20SIRET'> contactez notre équipe</a>.</p></div>"
      data-type="info"
    >
      <Icon svg="picto-info" />
    </span>
  )
}

export default TooltipInvalidSiret
