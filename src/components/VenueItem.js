import React from 'react'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'
import { pluralize } from '../utils/string'

const VenueItem = ({
  venue,
}) => {
  const {
    address,
    id,
    managingOffererId,
    name,
  } = (venue || {})

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
            <NavLink to={`/offres/nouveau?lieu=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' /> Créer une offre
            </NavLink>
          </li>
          <li>
            {
              venue.nOccasions > 0 ? (
                <li key={1}>
                  <NavLink to={`/offres?lieu=${id}`} className='has-text-primary'>
                    <Icon svg='ico-offres-r' />
                    { pluralize(venue.nOccasions, 'offres') }
                  </NavLink>
                </li>
              ) : (
                <li key={2}>0 offre</li>
              )
            }
          </li>
          <li>
            <p className="has-text-grey">{address}</p>
          </li>
        </ul>
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
