/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import { pluralize } from 'utils/pluralize'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const OffererItem = ({ offerer, physicalVenues, venues, isVenueCreationAvailable }) => {
  const { id, name, nOffers } = offerer || {}
  const detailsPath = `/accueil?structure=${id}`

  let createOfferLink = `/offres/creation?structure=${id}`
  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  if (venues.length === 1) {
    createOfferLink = `/offres/creation?structure=${id}&lieu=${venues[0].id}`
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${id}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <li className="offerer-item">
      <div className="list-content">
        <p className="name">
          <Link to={detailsPath}>
            {name}
          </Link>
        </p>

        <ul className="actions">
          <li id="create-offer-action">
            <Link
              className="has-text-primary"
              to={createOfferLink}
            >
              <AddOfferSvg />
              Nouvelle offre
              {canCreateOnlyVirtualOffer && ' numérique'}
            </Link>
          </li>

          {nOffers && nOffers > 0 ? (
            <li className="count-offers-action">
              <Link
                className="has-text-primary"
                to={`/offres?structure=${id}`}
              >
                <Icon svg="ico-offres-r" />
                {pluralize(nOffers, 'offres')}
              </Link>
            </li>
          ) : (
            <li className="count-offers-action">
              0 offre
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
              Nouveau lieu
            </Link>
          </li>
        </ul>
      </div>
      <div className="caret">
        <Link to={detailsPath}>
          <Icon svg="ico-next-S" />
        </Link>
      </div>
    </li>
  )
}

OffererItem.defaultProps = {
  offerer: {},
  physicalVenues: [],
  venues: [],
}

OffererItem.propTypes = {
  isVenueCreationAvailable: PropTypes.bool.isRequired,
  offerer: PropTypes.shape(),
  physicalVenues: PropTypes.arrayOf(PropTypes.shape()),
  venues: PropTypes.arrayOf(PropTypes.shape()),
}

export default OffererItem
