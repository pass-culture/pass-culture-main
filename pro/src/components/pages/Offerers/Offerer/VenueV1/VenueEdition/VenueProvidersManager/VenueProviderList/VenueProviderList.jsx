import AllocineProviderItem from '../AllocineProviderItem/AllocineProviderItem'
import PropTypes from 'prop-types'
import React from 'react'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'
import { isAllocineProvider } from 'components/pages/Offers/domain/localProvider'

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
