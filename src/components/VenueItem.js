import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'
import Icon from './layout/Icon'

const VenueItem = ({
  address,
  id,
  managingOffererId,
  name
}) => {
  const showPath = `/structures/${managingOffererId}/lieux/${id}`
  return (
    <li className="venue-item">
      <div className='picto'>
        <Icon svg='picto-structure' />
      </div>
      <div className="list-content">
        <p className="name">
          <NavLink to={showPath}>{name}</NavLink>
        </p>
        <ul className='actions'>
          <li>
            <NavLink to={`/offres?venueId=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' /> ?? offres
            </NavLink>
          </li>
          <li>
            <p className="has-text-grey">{address}</p>
          </li>
        </ul>
        {false && <nav className="level">
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
                </nav>}
      </div>
      <div className='caret'>
        <NavLink to={showPath}>
          <Icon svg='ico-next-S' />
        </NavLink>
      </div>
    </li>
  )
}

export default VenueItem
