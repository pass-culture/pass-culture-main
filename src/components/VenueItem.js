import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'

const VenueItem = ({
  address,
  id,
  managingOffererId,
  name
}) => {
  const src = `${THUMBS_URL}/structures//lieux/${id}`
  return (
    <article className="venue-item media">
      <figure className="media-left">
        <div className="image is-64x64" style={{
          backgroundImage: `url('${src}')`,
          backgroundSize: 'cover'
        }} />
      </figure>
      <div className="media-content">
        <div className="content">
          <p className="title">
            <strong>{name}</strong>
          </p>
          <p className="subtitle">
            {address}
          </p>
        </div>
        <nav className="level">
          <NavLink to={`/structures/${managingOffererId}/lieux/${id}`}>
            <button className="button is-primary level-item">
              Configurer
            </button>
          </NavLink>
          <NavLink to={`/structures/${managingOffererId}/lieux/${id}/offres`}>
            <button className="button is-primary level-item">
              Créer des offres
            </button>
          </NavLink>
          <NavLink to={`/structures/${managingOffererId}/lieux/${id}/fournisseurs/nouveau`}>
            <button className="button is-primary level-item">
              Importer des offres
            </button>
          </NavLink>
        </nav>
      </div>
    </article>
  )
}

export default VenueItem
