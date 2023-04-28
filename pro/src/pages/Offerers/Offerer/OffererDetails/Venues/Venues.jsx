import PropTypes from 'prop-types'
import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { ReactComponent as PlusCircleIcon } from 'icons/ico-plus-circle.svg'
import { ButtonLink } from 'ui-kit'
import { UNAVAILABLE_ERROR_PAGE } from 'utils/routes'

import VenueItem from './VenueItem/VenueItem'

const Venues = ({ venues, offererId }) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  const { logEvent } = useAnalytics()
  return (
    <div className="section op-content-section">
      <h2 className="main-list-title">Lieux</h2>
      <ul className="main-list venues-list">
        {venues.map(venue => (
          <VenueItem
            key={venue.nonHumanizedId}
            venue={venue}
            offererId={offererId}
          />
        ))}
      </ul>
      <div className="has-text-centered">
        <ButtonLink
          link={{
            to: venueCreationUrl,
            isExternal: false,
          }}
          onClick={() => {
            logEvent?.(Events.CLICKED_ADD_VENUE_IN_OFFERER, {
              from: location.pathname,
            })
          }}
          Icon={PlusCircleIcon}
        >
          Ajouter un lieu
        </ButtonLink>
      </div>
    </div>
  )
}
Venues.propTypes = {
  offererId: PropTypes.number.isRequired,
  venues: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Venues
