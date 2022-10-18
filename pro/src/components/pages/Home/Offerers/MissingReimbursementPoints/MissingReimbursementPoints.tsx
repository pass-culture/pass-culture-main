import React from 'react'

import { Banner } from 'ui-kit'

const MissingReimbursementPoints = () => {
  return (
    <div className="h-card-content">
      <Banner>
        <h4 className="banner-title">Coordonnées bancaires</h4>
        Certains de vos lieux ne sont pas rattachés à des coordonnées bancaires.
        Pour percevoir les remboursements liés aux offres de ces lieux, veuillez
        renseigner des coordonnées bancaires.
      </Banner>
    </div>
  )
}

export default MissingReimbursementPoints
