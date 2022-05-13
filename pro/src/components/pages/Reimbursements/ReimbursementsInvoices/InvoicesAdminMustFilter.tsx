import { ReactComponent as OfferCardEuro } from 'icons/offer-card-euro.svg'
import React from 'react'

const InvoicesAdminMustFilter = (): JSX.Element => {
  return (
    <div className="no-refunds admin-view">
      <OfferCardEuro />
      <p className="admin-view-description">
        Pour visualiser vos justificatifs de remboursement, veuillez
        sélectionner un ou plusieurs des filtres précédents et cliquer sur
        «&nbsp;Lancer la recherche&nbsp;»
      </p>
    </div>
  )
}

export default InvoicesAdminMustFilter
