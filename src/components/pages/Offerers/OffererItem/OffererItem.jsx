import { Icon } from 'pass-culture-shared'
import React from 'react'
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import { UNAVAILABLE_ERROR_PAGE } from '../../../../utils/routes'
import { pluralize } from '../../../../utils/pluralize'

const OffererItem = ({ offerer, physicalVenues, venues, isVenueCreationAvailable }) => {
  const { id, name, nOffers, isValidated } = offerer || {}
  const showPath = `/structures/${id}`

  let createOfferLink = `/offres/creation?structure=${id}`
  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  if (venues.length < 2) {
    createOfferLink = `/offres/creation?structure=${id}&lieu=${venues[0].id}`
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${id}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <li className="offerer-item">
      <div className="list-content">
        <p className="name">
          <Link to={showPath}>
            {name}
          </Link>
        </p>
        {!isValidated && (
          <p
            className="is-italic mb12"
            id="offerer-item-validation"
          >
            {'Structure en cours de validation par l’équipe pass Culture.'}
          </p>
        )}

        <ul className="actions">
          <li id="create-offer-action">
            <Link
              className="has-text-primary"
              to={createOfferLink}
            >
              <Icon svg="ico-offres-r" />
              {'Nouvelle offre'}
              {canCreateOnlyVirtualOffer && ' numérique'}
            </Link>
          </li>

          {nOffers && nOffers > 0 ? (
            <li className="count-offers-action">
              {pluralize(nOffers, 'offres')}
            </li>
          ) : (
            <li className="count-offers-action">
              {'0 offre'}
            </li>
          )}

          <li id="count-venues-action">
            <Link
              className="has-text-primary"
              to={`/structures/${id}/`}
            >
              <Icon svg="ico-venue" />
              {pluralize(physicalVenues.length, 'lieux')}
            </Link>
          </li>

          <li id="create-venue-action">
            <Link
              className="has-text-primary"
              to={venueCreationUrl}
            >
              <Icon svg="ico-venue-r" />
              {'Nouveau lieu'}
            </Link>
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

OffererItem.defaultProps = {
  physicalVenues: [],
  venues: [],
}

OffererItem.propTypes = {
  physicalVenues: PropTypes.arrayOf(PropTypes.shape()),
  venues: PropTypes.arrayOf(PropTypes.shape()),
}

export default OffererItem
