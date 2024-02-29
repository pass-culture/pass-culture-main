import React, { useState } from 'react'

import { VenueProviderResponse, GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { Providers } from 'core/Venue/types'
import AddVenueProviderButton from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/AddVenueProviderButton'
import VenueProviderList from 'pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/VenueProviderList/VenueProviderList'

interface OffersSynchronization {
  provider: Providers[]
  venueProvider: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

const OffersSynchronization = ({
  venue,
  provider,
  venueProvider,
}: OffersSynchronization) => {
  const [venueProviders, setVenueProviders] =
    useState<VenueProviderResponse[]>(venueProvider)

  const afterVenueProviderEdit = (
    editedVenueProvider: VenueProviderResponse
  ) => {
    const newVenueProviders = venueProviders.map((venueProvider) =>
      venueProvider.id === editedVenueProvider.id
        ? editedVenueProvider
        : venueProvider
    )
    setVenueProviders(newVenueProviders)
  }

  const afterVenueProviderDelete = (deletedVenueProviderId: number) => {
    const newVenueProviders = venueProviders.filter(
      (venueProvider) => venueProvider.id !== deletedVenueProviderId
    )
    setVenueProviders(newVenueProviders)
  }
  return (
    <FormLayout.Section
      title="Gestion des synchronisations"
      description="Vous pouvez synchroniser votre lieu avec un logiciel tiers afin de faciliter la gestion de vos offres et de vos réservations."
    >
      <FormLayout.Row>
        {venueProviders.length > 0 ? (
          <VenueProviderList
            afterVenueProviderDelete={afterVenueProviderDelete}
            afterVenueProviderEdit={afterVenueProviderEdit}
            venue={venue}
            venueProviders={venueProviders}
          />
        ) : (
          <AddVenueProviderButton
            providers={provider}
            setVenueProviders={setVenueProviders}
            venue={venue}
          />
        )}
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default OffersSynchronization
