import React from 'react'

import { VenueProviderResponse } from 'apiClient/v1'
import { IVenue } from 'core/Venue/types'

import VenueProviderItemV2 from '../VenueProviderItemV2/VenueProviderItemV2'

export interface IVenueProviderListV2Props {
  afterVenueProviderDelete: (deletedVenueProvider: string) => void
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  venue: IVenue
  venueProviders: VenueProviderResponse[]
}

const VenueProviderListV2 = ({
  afterVenueProviderDelete,
  afterVenueProviderEdit,
  venue,
  venueProviders,
}: IVenueProviderListV2Props): JSX.Element => {
  return (
    <ul className="provider-list">
      {venueProviders.map(venueProvider => (
        <VenueProviderItemV2
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

export default VenueProviderListV2
