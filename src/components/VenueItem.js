import { Icon } from 'pass-culture-shared'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'

import { pluralize } from '../utils/string'

const VenueItem = ({ venue }) => {
  const { address, city, id, managingOffererId, name, postalCode } = venue || {}

  const showPath = `/structures/${managingOffererId}/lieux/${id}`
  return (
    <li className="venue-item">
      <div className="picto">
        <Icon svg="ico-venue" />
      </div>
      <div className="list-content">
        <p className="name">
          <NavLink
            id={`a-${name ? name.toLowerCase().replace(/\s/g, '-') : ''}`}
            to={showPath}>
            {name}
          </NavLink>
        </p>
        <ul className="actions">
          <li>
            <NavLink
              to={`/offres/nouveau?lieu=${id}`}
              className="has-text-primary">
              <Icon svg="ico-offres-r" /> Créer une offre
            </NavLink>
          </li>
          {venue.nOccasions > 0 ? (
            <li>
              <NavLink to={`/offres?lieu=${id}`} className="has-text-primary">
                <Icon svg="ico-offres-r" />
                {pluralize(venue.nOccasions, 'offres')}
              </NavLink>
            </li>
          ) : (
            <li>0 offre</li>
          )}
          <li>
            <Dotdotdot className="has-text-grey" clamp={2}>
              {address} {postalCode} {city}
            </Dotdotdot>
          </li>
        </ul>
      </div>
      <div className="caret">
        <NavLink to={showPath}>
          <Icon svg="ico-next-S" />
        </NavLink>
      </div>
    </li>
  )
}

export default VenueItem
