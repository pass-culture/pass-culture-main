import React from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

const InvoicesServerError = (): JSX.Element => {
  return (
    <div className="no-refunds">
      <SvgIcon
        alt=""
        src={strokeWipIcon}
        className="no-refunds-icon"
        viewBox="0 0 200 156"
      />
      <p className="no-refunds-title">Une erreur est survenue</p>
      <p className="no-refunds-description">Veuillez réessayer plus tard</p>
    </div>
  )
}

export default InvoicesServerError
