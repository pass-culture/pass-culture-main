import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

const NoOffers = () => {
  return (
    <div className="no-search-results">
      <Icon className="image" svg="ico-ticket-gray" />

      <p className="highlight">Aucune offre</p>
      <p>Vous n’avez pas encore créé d’offre.</p>

      <Link className="primary-button with-icon" to="/offre/creation">
        <AddOfferSvg />
        Créer ma première offre
      </Link>
    </div>
  )
}

export default NoOffers
