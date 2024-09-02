import cn from 'classnames'
import React from 'react'

import { VenueProviderResponse, GetVenueResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'

import { AddVenueProviderButton } from './AddVenueProviderButton'
import style from './OffersSynchronization.module.scss'
import { VenueProviderCard } from './VenueProviderList/VenueProviderCard'

interface OffersSynchronization {
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const OffersSynchronization = ({
  venue,
  venueProviders,
}: OffersSynchronization) => {
  return (
    <FormLayout>
      <FormLayout.Section
        title="Gestion des synchronisations"
        description="Vous pouvez synchroniser votre lieu avec un logiciel tiers afin de faciliter la gestion de vos offres et de vos réservations."
      >
        <FormLayout.Row
          className={cn(style['venue-providers'], 'form-layout-actions')}
        >
          {venueProviders.map((venueProvider) => (
            <VenueProviderCard
              key={venueProvider.id}
              venueProvider={venueProvider}
              venue={venue}
              venueDepartmentCode={venue.departementCode}
              offererId={venue.managingOfferer.id}
            />
          ))}
        </FormLayout.Row>
        <FormLayout.Row>
          <AddVenueProviderButton
            venue={venue}
            linkedProviders={venueProviders.map(({ provider }) => provider)}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </FormLayout>
  )
}
