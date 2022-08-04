import PropTypes from 'prop-types'
import React from 'react'

import { isAllocineProvider, isCinemaProvider } from 'core/Providers'

import AllocineProviderItem from '../AllocineProviderItem/AllocineProviderItem'
import { CinemaProviderItem } from '../CinemaProviderItem/CinemaProviderItem'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'

const VenueProviderList = ({
  afterVenueProviderEdit,
  venue,
  venueProviders,
}) => {
  return (
    <ul className="provider-list">
      {venueProviders.map(venueProvider =>
        isAllocineProvider(venueProvider.provider) ? (
          <AllocineProviderItem
            afterVenueProviderEdit={afterVenueProviderEdit}
            key={venueProvider.id}
            venueDepartmentCode={venue.departementCode}
            venueProvider={venueProvider}
          />
        ) : isCinemaProvider(venueProvider.provider) ? (
          <CinemaProviderItem
            afterVenueProviderEdit={afterVenueProviderEdit}
            key={venueProvider.id}
            venueDepartementCode={venue.departementCode}
            venueProvider={venueProvider}
          />
        ) : (
          <VenueProviderItem
            key={venueProvider.id}
            venueDepartmentCode={venue.departementCode}
            venueProvider={venueProvider}
          />
        )
      )}
    </ul>
  )
}

VenueProviderList.defaultProps = {
  venueProviders: [],
}

VenueProviderList.propTypes = {
  afterVenueProviderEdit: PropTypes.func.isRequired,
  venue: PropTypes.shape({
    departementCode: PropTypes.string.isRequired,
  }).isRequired,
  venueProviders: PropTypes.arrayOf(PropTypes.shape()),
}

export default VenueProviderList
