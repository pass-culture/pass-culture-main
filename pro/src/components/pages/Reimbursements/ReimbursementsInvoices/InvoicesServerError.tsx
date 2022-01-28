import React from 'react'

import { ReactComponent as UnavailablePageSVG } from 'icons/ico-unavailable-page.svg'

const InvoicesServerError = (): JSX.Element => {
  return (
    <div className="no-refunds">
      <UnavailablePageSVG />
      <p className="no-refunds-title">Une erreur est survenue</p>
      <p className="no-refunds-description">Veuillez réessayer plus tard</p>
    </div>
  )
}

export default InvoicesServerError
