import React from 'react'

import { ReactComponent as OfferCardEuro } from 'icons/offer-card-euro.svg'

const NoInvoicesYet = (): JSX.Element => {
  return (
    <div className="no-refunds admin-view">
      <OfferCardEuro />
      <p className="no-refunds-title">
        Vous n’avez pas encore de justificatifs de remboursement disponibles
      </p>
      <p className="no-refunds-description">
        Lorsqu’ils auront été édités, vous pourrez les télécharger ici
      </p>
    </div>
  )
}

export default NoInvoicesYet
