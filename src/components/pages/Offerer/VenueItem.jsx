import { Icon, pluralize } from 'pass-culture-shared'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { NavLink } from 'react-router-dom'

const formatVenueNameOrPublicName = value => {
  return value ? value.toLowerCase().replace(/\s/g, '-') : ''
}

const VenueItem = ({ venue }) => {
  const { address, city, id, managingOffererId, name, postalCode, publicName } =
    venue || {}

  const showPath = `/structures/${managingOffererId}/lieux/${id}`
  return (
    <li className="venue-item">
      <div className="picto">
        <Icon svg="ico-venue" />
      </div>
      <div className="list-content">
        <p className="name">
          <NavLink
            id={`a-${
              publicName
                ? formatVenueNameOrPublicName(publicName)
                : formatVenueNameOrPublicName(name)
            }`}
            to={showPath}>
            {publicName || name}
          </NavLink>
        </p>
        <ul className="actions">
          <li>
            <NavLink
              to={`/offres/creation?lieu=${id}`}
              className="has-text-primary">
              <Icon svg="ico-offres-r" /> Créer une offre
            </NavLink>
          </li>
          {venue.nOffers > 0 ? (
            <li>
              <NavLink to={`/offres?lieu=${id}`} className="has-text-primary">
                <Icon svg="ico-offres-r" />
                {pluralize(venue.nOffers, 'offres')}
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
