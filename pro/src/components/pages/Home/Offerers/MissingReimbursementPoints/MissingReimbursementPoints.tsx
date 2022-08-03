import React from 'react'

import Icon from 'components/layout/Icon'
import { Banner } from 'ui-kit'

const MissingReimbursementPoints = () => {
  return (
    <>
      <h3 className="h-card-secondary-title">
        Coordonnées bancaires
        <Icon
          alt="Coordonnées bancaires manquantes"
          className="ico-bank-warning"
          svg="ico-alert-filled"
        />
      </h3>

      <div className="h-card-content">
        <Banner
          icon="ico-outer-pen"
          linkTitle="Renseigner des coordonnées bancaires"
        >
          Certains de vos lieux ne sont pas rattachés à des coordonnées
          bancaires. Pour percevoir les remboursements liés aux offres de ces
          lieux, veuillez renseigner des coordonnées bancaires.
        </Banner>
      </div>
    </>
  )
}

export default MissingReimbursementPoints
