import { Icon } from 'pass-culture-shared'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'
import { Link } from 'react-router-dom'
import { pluralize } from '../../../../../../utils/pluralize'

const buildLinkIdFromVenue = ({ publicName, name }) => {
  const nameToFormat = publicName || name
  return nameToFormat ? nameToFormat.toLowerCase().replace(/\s/g, '-') : ''
}

const VenueItem = ({ venue }) => {
  const { address, city, id, managingOffererId, name, postalCode, publicName } = venue || {}
  const showPath = `/structures/${managingOffererId}/lieux/${id}`

  return (
    <li className="venue-item">
      <div className="picto">
        <Icon svg="ico-venue" />
      </div>
      <div className="list-content">
        <p className="name">
          <Link
            id={`a-${buildLinkIdFromVenue(venue)}`}
            to={showPath}
          >
            {publicName || name}
          </Link>
        </p>
        <ul className="actions">
          <li>
            <Link
              className="has-text-primary"
              to={`/offres/creation?lieu=${id}&structure=${managingOffererId}`}
            >
              <Icon svg="ico-offres-r" />
              {' Créer une offre'}
            </Link>
          </li>
          {venue.nOffers > 0 ? (
            <li>
              <Link
                className="has-text-primary"
                to={`/offres?lieu=${id}`}
              >
                <Icon svg="ico-offres-r" />
                {pluralize(venue.nOffers, 'offres')}
              </Link>
            </li>
          ) : (
            <li>
              {'0 offre'}
            </li>
          )}
          <li>
            <Dotdotdot
              clamp={2}
              className="has-text-grey"
            >
              {`${address} ${postalCode} ${city}`}
            </Dotdotdot>
          </li>
        </ul>
      </div>
      <div className="caret">
        <Link to={showPath}>
          <Icon svg="ico-next-S" />
        </Link>
      </div>
    </li>
  )
}

export default VenueItem
