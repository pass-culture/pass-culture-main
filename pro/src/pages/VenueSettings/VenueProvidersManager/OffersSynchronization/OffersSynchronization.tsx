import cn from 'classnames'

import { GetVenueResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { AddVenueProviderButton } from 'pages/VenueSettings/VenueProvidersManager/AddVenueProviderButton'
import style from 'pages/VenueSettings/VenueProvidersManager/OffersSynchronization/OffersSynchronization.module.scss'
import { VenueProviderCard } from 'pages/VenueSettings/VenueProvidersManager/VenueProviderList/VenueProviderCard'

interface OffersSynchronizationProps {
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const OffersSynchronization = ({
  venue,
  venueProviders,
}: OffersSynchronizationProps) => {
  return (
    <FormLayout>
      <FormLayout.Section
        title="Gestion des synchronisations"
        description={`Vous pouvez synchroniser votre structure avec un logiciel tiers afin de faciliter la gestion de vos offres et de vos réservations.`}
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
