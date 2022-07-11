import { IAPIVenue } from 'core/Venue/types'
import { IVenueProviderApi } from '../../VenueProvidersManager/CinemaProviderItem/types'
import React from 'react'
import VenueProviderItemV2 from '../VenueProviderItemV2/VenueProviderItemV2'

export interface IVenueProviderListV2Props {
  afterVenueProviderDelete: (deletedVenueProvider: string) => void
  afterVenueProviderEdit: (editedVenueProvider: IVenueProviderApi) => void
  venue: IAPIVenue
  venueProviders: IVenueProviderApi[]
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
          venueDepartmentCode={venue.departementCode}
        />
      ))}
    </ul>
  )
}

export default VenueProviderListV2
