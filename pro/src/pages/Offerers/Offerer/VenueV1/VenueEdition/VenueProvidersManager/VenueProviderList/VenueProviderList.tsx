import React from 'react'

import { VenueProviderResponse } from 'apiClient/v1'
import { IVenue } from 'core/Venue/types'

import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'

interface VenueProviderListV2Props {
  afterVenueProviderDelete: (deletedVenueProvider: number) => void
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  venue: IVenue
  venueProviders: VenueProviderResponse[]
}

const VenueProviderList = ({
  afterVenueProviderDelete,
  afterVenueProviderEdit,
  venue,
  venueProviders,
}: VenueProviderListV2Props): JSX.Element => {
  return (
    <ul className="provider-list">
      {venueProviders.map(venueProvider => (
        <VenueProviderItem
          afterDelete={afterVenueProviderDelete}
          afterSubmit={afterVenueProviderEdit}
          key={venueProvider.id}
          venueProvider={venueProvider}
          venueDepartmentCode={venue.departmentCode}
        />
      ))}
    </ul>
  )
}

export default VenueProviderList
