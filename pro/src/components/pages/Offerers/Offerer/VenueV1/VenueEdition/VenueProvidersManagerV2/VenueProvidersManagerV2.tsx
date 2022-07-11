import * as pcapi from 'repository/pcapi/pcapi'
import React, { useEffect, useState } from 'react'
import AddVenueProviderButton from '../VenueProvidersManager/AddVenueProviderButton'
import { IAPIVenue } from 'core/Venue/types'
import { IVenueProviderApi } from '../VenueProvidersManager/CinemaProviderItem/types'
import Spinner from 'components/layout/Spinner'
import VenueProviderListV2 from './VenueProviderListV2/VenueProviderListV2'

export interface IVenueProvidersManagerV2Props {
  venue: IAPIVenue
}

const VenueProvidersManagerV2 = ({
  venue,
}: IVenueProvidersManagerV2Props): JSX.Element | null => {
  const [providers, setProviders] = useState([])
  const [venueProviders, setVenueProviders] = useState<IVenueProviderApi[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      const providersResponse = await pcapi.loadProviders(venue.id)
      setProviders(providersResponse)

      const venueProvidersResponse = await pcapi.loadVenueProviders(venue.id)
      setVenueProviders(venueProvidersResponse)
      setIsLoading(false)
    }
    fetchData()
  }, [venue.id])

  const afterVenueProviderEdit = (editedVenueProvider: IVenueProviderApi) => {
    const newVenueProviders = venueProviders.map(venueProvider =>
      venueProvider.id === editedVenueProvider.id
        ? editedVenueProvider
        : venueProvider
    )
    setVenueProviders(newVenueProviders)
  }

  const afterVenueProviderDelete = (deletedVenueProviderId: string) => {
    const newVenueProviders = venueProviders.filter(
      venueProvider => venueProvider.id !== deletedVenueProviderId
    )
    setVenueProviders(newVenueProviders)
  }

  if (!isLoading && !providers.length && !venueProviders.length) {
    return null
  }

  return (
    <div className="venue-providers-manager section">
      <h2 className="main-list-title">Synchronisation des offres</h2>

      {isLoading ? (
        <Spinner />
      ) : venueProviders.length > 0 ? (
        <VenueProviderListV2
          afterVenueProviderDelete={afterVenueProviderDelete}
          afterVenueProviderEdit={afterVenueProviderEdit}
          venue={venue}
          venueProviders={venueProviders}
        />
      ) : (
        <AddVenueProviderButton
          providers={providers}
          setVenueProviders={setVenueProviders}
          venue={venue}
        />
      )}
    </div>
  )
}

export default VenueProvidersManagerV2
