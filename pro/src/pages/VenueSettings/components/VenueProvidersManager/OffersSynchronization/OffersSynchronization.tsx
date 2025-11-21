import { useRef } from 'react'

import type {
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { AddVenueProviderButton } from '@/pages/VenueSettings/components/VenueProvidersManager/AddVenueProviderButton'
import { VenueProviderCard } from '@/pages/VenueSettings/components/VenueProvidersManager/VenueProviderList/VenueProviderCard'

import style from './OffersSynchronization.module.scss'

interface OffersSynchronizationProps {
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const OffersSynchronization = ({
  venue,
  venueProviders,
}: OffersSynchronizationProps) => {
  const selectSoftwareButtonRef = useRef<HTMLButtonElement>(null)

  return (
    <FormLayout>
      <FormLayout.Section
        title="Gestion des synchronisations"
        description={`Vous pouvez synchroniser votre structure avec un logiciel tiers afin de faciliter la gestion de vos offres et de vos réservations.`}
      >
        <FormLayout.Row className={style['venue-providers']}>
          {venueProviders.map((venueProvider) => (
            <VenueProviderCard
              key={venueProvider.id}
              venueProvider={venueProvider}
              venue={venue}
              venueDepartmentCode={venue.location?.departmentCode}
              offererId={venue.managingOfferer.id}
              selectSoftwareButtonRef={selectSoftwareButtonRef}
            />
          ))}
        </FormLayout.Row>
        <FormLayout.Row className={style['venue-providers-synchro']}>
          <AddVenueProviderButton
            venue={venue}
            linkedProviders={venueProviders.map(({ provider }) => provider)}
            selectSoftwareButtonRef={selectSoftwareButtonRef}
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </FormLayout>
  )
}
