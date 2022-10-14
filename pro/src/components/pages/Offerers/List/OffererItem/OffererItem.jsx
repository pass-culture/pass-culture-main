import PropTypes from 'prop-types'
import React from 'react'

import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as IconOffers } from 'icons/ico-offers.svg'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { ReactComponent as IcoVenue } from 'icons/ico-venue.svg'
import { ButtonLink } from 'ui-kit'
import { pluralize } from 'utils/pluralize'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

const OffererItem = ({ offerer }) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const { id: offererId, managedVenues: venues, name, nOffers } = offerer || {}

  const physicalVenues = venues.filter(venue => !venue.isVirtual)

  const detailsPath = `/accueil?structure=${offererId}`

  let createOfferLink = `/offre/creation?structure=${offererId}`
  const canCreateOnlyVirtualOffer = venues.length === 1 && venues[0].isVirtual

  if (venues.length === 1) {
    createOfferLink = `/offre/creation?structure=${offererId}&lieu=${venues[0].id}`
  }

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  return (
    <li className="offerer-item">
      <div className="list-content">
        <ButtonLink
          className="name"
          link={{
            to: detailsPath,
            isExternal: false,
          }}
        >
          {name}
        </ButtonLink>

        <ul className="actions">
          <li id="create-offer-action">
            <ButtonLink
              className="has-text-primary"
              link={{
                to: createOfferLink,
                isExternal: false,
              }}
              Icon={PlusCircleIcon}
            >
              Nouvelle offre
              {canCreateOnlyVirtualOffer && ' numérique'}
            </ButtonLink>
          </li>

          {nOffers !== 0 ? (
            <li className="count-offers-action">
              <ButtonLink
                className="has-text-primary"
                link={{
                  to: `/offres?structure=${offererId}`,
                  isExternal: false,
                }}
              >
                <IconOffers className="counter-offers-icon" />{' '}
                {
                  // Count is negative if offerer has too much venues and
                  // probably too much offers to count.
                  nOffers > 0 ? pluralize(nOffers, 'offres') : `offres`
                }
                {nOffers >= 100 ? '+' : ''}
              </ButtonLink>
            </li>
          ) : (
            <li className="count-offers-action">0 offre</li>
          )}

          <li id="count-venues-action">
            <ButtonLink
              className="has-text-primary"
              link={{
                to: `/structures/${offererId}/`,
                isExternal: false,
              }}
              Icon={IcoVenue}
            >
              {pluralize(physicalVenues.length, 'lieux')}
            </ButtonLink>
          </li>

          <li id="create-venue-action">
            <ButtonLink
              className="has-text-primary"
              link={{
                to: venueCreationUrl,
                isExternal: false,
              }}
              Icon={IcoVenue}
            >
              Nouveau lieu
            </ButtonLink>
          </li>
        </ul>
      </div>
    </li>
  )
}

OffererItem.defaultProps = {
  offerer: {},
}

OffererItem.propTypes = {
  offerer: PropTypes.shape(),
}

export default OffererItem
