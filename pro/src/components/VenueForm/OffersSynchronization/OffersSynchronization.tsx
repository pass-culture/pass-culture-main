import React, { useEffect, useState } from 'react'

import { VenueProviderResponse } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { IProviders, IVenue } from 'core/Venue/types'
import AddVenueProviderButton from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/AddVenueProviderButton'
import VenueProviderList from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/VenueProviderList/VenueProviderList'
import Spinner from 'ui-kit/Spinner/Spinner'

interface OffersSynchronization {
  provider: IProviders[]
  venueProvider: VenueProviderResponse[]
  venue: IVenue
}

const OffersSynchronization = ({
  venue,
  provider,
  venueProvider,
}: OffersSynchronization) => {
  const [isLoading, setIsLoading] = useState(false)
  const [providers, setProviders] = useState(provider)
  const [venueProviders, setVenueProviders] =
    useState<VenueProviderResponse[]>(venueProvider)
  useEffect(() => {
    setProviders(providers)
    setVenueProviders(venueProviders)
    setIsLoading(false)
  }, [venue])

  const afterVenueProviderEdit = (
    editedVenueProvider: VenueProviderResponse
  ) => {
    const newVenueProviders = venueProviders.map(venueProvider =>
      venueProvider.id === editedVenueProvider.id
        ? editedVenueProvider
        : venueProvider
    )
    setVenueProviders(newVenueProviders)
  }

  const afterVenueProviderDelete = (deletedVenueProviderId: number) => {
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
          <VenueProviderList
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
