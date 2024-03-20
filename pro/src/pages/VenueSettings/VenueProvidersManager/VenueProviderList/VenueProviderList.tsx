import React from 'react'

import { VenueProviderResponse, GetVenueResponseModel } from 'apiClient/v1'

import { VenueProviderItem } from './VenueProviderItem'

interface VenueProviderListProps {
  afterVenueProviderDelete: (deletedVenueProvider: number) => void
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  venue: GetVenueResponseModel
  venueProviders: VenueProviderResponse[]
}

export const VenueProviderList = ({
  afterVenueProviderDelete,
  afterVenueProviderEdit,
  venue,
  venueProviders,
}: VenueProviderListProps): JSX.Element => {
  return (
    <ul>
      {venueProviders.map((venueProvider) => (
        <VenueProviderItem
          afterDelete={afterVenueProviderDelete}
          afterSubmit={afterVenueProviderEdit}
          key={venueProvider.id}
          venueProvider={venueProvider}
          venueDepartmentCode={venue.departementCode}
          offererId={venue.managingOfferer.id}
        />
      ))}
    </ul>
  )
}
