import { Icon, pluralize } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'
import PropTypes from 'prop-types'

const OffererItem = ({ offerer, physicalVenues, venues }) => {
  const { id, name, nOffers, isValidated } = offerer || {}
  const showPath = `/structures/${id}`

  let createOfferLink = `/offres/creation?structure=${id}`
  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  if (venues.length < 2) {
    createOfferLink = `/offres/creation?structure=${id}&lieu=${venues[0].id}`
  }

  return (
    <li className="offerer-item">
      <div className="list-content">
        <p className="offerer-name">
          <NavLink to={showPath}>
            {name}
          </NavLink>
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
            <NavLink
              className="has-text-primary"
              to={createOfferLink}
            >
              <Icon svg="ico-offres-r" />
              {'Nouvelle offre'}
              {canCreateOnlyVirtualOffer && ' numérique'}
            </NavLink>
          </li>

          {nOffers && nOffers > 0 ? (
            <li className="count-offers-action">
              <NavLink
                className="has-text-primary"
                to={`/offres?structure=${id}`}
              >
                <Icon svg="ico-offres-r" />
                {pluralize(nOffers, 'offres')}
              </NavLink>
            </li>
          ) : (
            <li className="count-offers-action">
              {'0 offre'}
            </li>
          )}

          <li id="count-venues-action">
            <NavLink
              className="has-text-primary"
              to={`/structures/${id}/`}
            >
              <Icon svg="ico-venue" />
              {pluralize(physicalVenues.length, 'lieux')}
            </NavLink>
          </li>

          <li id="create-venue-action">
            <NavLink
              className="has-text-primary"
              to={`/structures/${id}/lieux/creation`}
            >
              <Icon svg="ico-venue-r" />
              {'Nouveau lieu'}
            </NavLink>
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

OffererItem.defaultProps = {
  physicalVenues: [],
  venues: [],
}

OffererItem.propTypes = {
  physicalVenues: PropTypes.arrayOf(PropTypes.shape()),
  venues: PropTypes.arrayOf(PropTypes.shape()),
}

export default OffererItem
