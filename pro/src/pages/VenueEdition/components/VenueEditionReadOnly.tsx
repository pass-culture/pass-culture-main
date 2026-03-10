import { useMemo } from 'react'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from '../VenueEdition.module.scss'
import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'
import { OpeningHoursAndAddressReadOnly } from './OpeningHoursAndAddressReadOnly/OpeningHoursAndAddressReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const { data } = useEducationalDomains()
  const isVolunteeringActive = useActiveFeature('WIP_VOLUNTEERING')

  const mapVenueDomains = useMemo(() => {
    if (data.length === 0) {
      return null
    }

    const domains = venue.collectiveDomains.map((domain) => {
      const apiValue = data.find(
        (educationalDomain) => educationalDomain.id === domain.id
      )
      assertOrFrontendError(
        apiValue,
        `CulturalDomain with name ${domain.name} not found`
      )
      return apiValue.name
    })

    return domains.length > 0 ? domains : ['Non renseigné']
  }, [data, venue.collectiveDomains])

  return (
    <SummarySection
      title="Vos informations"
      editLink={getVenuePagePathToNavigateTo(
        venue.managingOfferer.id,
        venue.id,
        '/edition'
      )}
    >
      {isVolunteeringActive && (
        <SummarySubSection title="Bénévolat" shouldShowDivider={false}>
          <SummaryDescriptionList
            descriptions={[
              {
                title: 'Lien vers votre page organisation jeveuxaider.gouv.fr',
                text: venue.volunteeringUrl ?? 'Non renseigné',
              },
            ]}
          />
        </SummarySubSection>
      )}
      <SummarySubSection title="Accueil du public" shouldShowDivider={false}>
        <div className={styles['opentopublic-label']}>
          Accueil du public dans la structure :{' '}
          {venue.isOpenToPublic ? 'Oui' : 'Non'}
        </div>

        {venue.isOpenToPublic && (
          <>
            <OpeningHoursAndAddressReadOnly
              openingHours={venue.openingHours}
              address={venue.location}
            />
            <AccessibilityReadOnly venue={venue} />
          </>
        )}
      </SummarySubSection>
      <SummarySubSection
        title="À propos de votre activité"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            ...(venue.activity
              ? [
                  {
                    title: 'Activité',
                    text: getActivityLabel(venue.activity),
                  },
                ]
              : []),
            ...(mapVenueDomains
              ? [
                  {
                    title: pluralizeFr(
                      mapVenueDomains.length,
                      'Domaine d’activité',
                      'Domaines d’activité'
                    ),
                    text: mapVenueDomains.join(', '),
                  },
                ]
              : []),
            {
              title: 'Description',
              text: venue.description ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
      <SummarySubSection
        title="Informations de contact"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Téléphone',
              text: venue.contact?.phoneNumber ?? 'Non renseigné',
            },
            {
              title: 'Adresse e-mail',
              text: venue.contact?.email ?? 'Non renseignée',
            },
            {
              title: 'URL de votre site web',
              text: venue.contact?.website ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
    </SummarySection>
  )
}
