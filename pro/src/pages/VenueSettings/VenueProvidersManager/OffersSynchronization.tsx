import React from 'react'

import { VenueProviderResponse, GetVenueResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'

import { AddVenueProviderButton } from './AddVenueProviderButton'
import { VenueProviderItem } from './VenueProviderList/VenueProviderItem'

interface OffersSynchronization {
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const OffersSynchronization = ({
  venue,
  venueProviders,
}: OffersSynchronization) => {
  return (
    <FormLayout mediumWidthActions>
      <FormLayout.Section
        title="Gestion des synchronisations"
        description="Vous pouvez synchroniser votre lieu avec un logiciel tiers afin de faciliter la gestion de vos offres et de vos réservations."
      >
        <FormLayout.Row>
          {venueProviders.length > 0 ? (
            <ul>
              {venueProviders.map((venueProvider) => (
                <VenueProviderItem
                  key={venueProvider.id}
                  venueProvider={venueProvider}
                  venue={venue}
                  venueDepartmentCode={venue.departementCode}
                  offererId={venue.managingOfferer.id}
                />
              ))}
            </ul>
          ) : (
            <AddVenueProviderButton venue={venue} />
          )}
        </FormLayout.Row>
      </FormLayout.Section>
    </FormLayout>
  )
}
