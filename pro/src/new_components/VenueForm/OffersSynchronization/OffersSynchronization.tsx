import React, { useEffect, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import AddVenueProviderButton from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/AddVenueProviderButton'
import { IVenueProviderApi } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/CinemaProviderItem/types'
import VenueProviderListV2 from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManagerV2/VenueProviderListV2/VenueProviderListV2'
import { IProviders, IVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'

interface IOffersSynchronization {
  provider: IProviders[]
  venueProvider: IVenueProviderApi[]
  venue: IVenue
}

const OffersSynchronization = ({
  venue,
  provider,
  venueProvider,
}: IOffersSynchronization) => {
  const [isLoading, setIsLoading] = useState(false)
  const [providers, setProviders] = useState(provider)
  const [venueProviders, setVenueProviders] =
    useState<IVenueProviderApi[]>(venueProvider)
  useEffect(() => {
    setProviders(providers)
    setVenueProviders(venueProviders)
    setIsLoading(false)
  }, [venue])

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
  return (
    <FormLayout.Section title="Synchronisation des offres">
      <FormLayout.Row>
        {isLoading && <Spinner />}
        {venueProviders.length > 0 ? (
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
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default OffersSynchronization
