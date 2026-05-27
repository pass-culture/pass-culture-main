import { useRef } from 'react'

import type {
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import { AddVenueProviderButton } from '@/pages/VenueSettings/components/VenueProvidersManager/AddVenueProviderButton'
import { VenueProviderCard } from '@/pages/VenueSettings/components/VenueProvidersManager/VenueProviderList/VenueProviderCard'

import styles from './SynchronizationConnexions.module.scss'

interface SynchronizationConnexionsProps {
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const SynchronizationConnexions = ({
  venue,
  venueProviders,
}: SynchronizationConnexionsProps) => {
  const selectSoftwareButtonRef = useRef<HTMLButtonElement>(null)

  return (
    <FormLayout>
      <FormLayout.Section title="Gestion des synchronisations">
        {venueProviders.length > 0 ? (
          <FormLayout.Row className={styles['venue-providers']} lgSpaceAfter>
            {venueProviders.map((venueProvider) => (
              <VenueProviderCard
                key={venueProvider.id}
                venueProvider={venueProvider}
                venue={venue}
                venueDepartmentCode={venue.location?.departmentCode}
                selectSoftwareButtonRef={selectSoftwareButtonRef}
              />
            ))}
          </FormLayout.Row>
        ) : (
          <FormLayout.Row lgSpaceAfter>
            <Banner
              title="Vous pouvez donner les accès à vos logiciels tiers pour qu'ils se synchronisent avec le pass Culture, afin de faciliter la gestion de vos offres et réservations."
              variant={BannerVariants.DEFAULT}
              actions={[
                {
                  label: 'Accéder à la documentation',
                  icon: fullLinkIcon,
                  href: 'https://passcultureapp.notion.site/Synchronisez-votre-logiciel-avec-le-pass-Culture-5eeb9cf86fe0457bbe479ad303daefd4',
                  type: 'link',
                  isExternal: true,
                },
              ]}
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row className={styles['venue-providers-synchro']}>
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
