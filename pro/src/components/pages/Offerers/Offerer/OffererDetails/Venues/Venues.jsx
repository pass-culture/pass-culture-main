import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
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
          <VenueItem key={venue.id} venue={venue} />
        ))}
      </ul>
      <div className="has-text-centered">
        <Link
          className="tertiary-link"
          to={venueCreationUrl}
          onClick={() => {
            logEvent?.(Events.CLICKED_ADD_VENUE_IN_OFFERER, {
              from: location.pathname,
            })
          }}
        >
          + Ajouter un lieu
        </Link>
      </div>
    </div>
  )
}
Venues.propTypes = {
  offererId: PropTypes.string.isRequired,
  venues: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Venues
