import type { GetVenueResponseModel } from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

import { AccessibilityReadOnly } from './AccessibilityReadOnly/AccessibilityReadOnly'
import { OpeningHoursAndAddressReadOnly } from './OpeningHoursAndAddressReadOnly/OpeningHoursAndAddressReadOnly'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isCulturalDomainsEnabled = useActiveFeature(
    'WIP_VENUE_CULTURAL_DOMAINS'
  )

  const { data } = useEducationalDomains()

  const aboutSectionDescription = [
    {
      title: 'Description',
      text: venue.description ?? 'Non renseignée',
    },
    ...(venue.activity
      ? [
          {
            title: 'Activité',
            text: getActivityLabel(venue.activity),
          },
        ]
      : []),
  ]
  if (isCulturalDomainsEnabled && data.length > 0) {
    const venueDomains = venue.collectiveDomains.map((domain) => {
      const apiValue = data.find(
        (educationalDomain) => educationalDomain.id === domain.id
      )
      assertOrFrontendError(
        apiValue,
        `CulturalDomain with name ${domain.name} not found`
      )

      return apiValue.name
    })
    aboutSectionDescription.push({
      title: 'Domaine(s) d’activité',
      text: venueDomains?.join(', ') || 'Non renseignés',
    })
  }
  const aboutSection = (
    <SummarySubSection
      title="À propos de votre activité"
      shouldShowDivider={false}
    >
      <SummaryDescriptionList descriptions={aboutSectionDescription} />
    </SummarySubSection>
  )

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={getVenuePagePathToNavigateTo(
        venue.managingOfferer.id,
        venue.id,
        '/edition'
      )}
    >
      {!isCulturalDomainsEnabled && aboutSection}
      <SummarySubSection title="Accueil du public" shouldShowDivider={false}>
        {!venue.isOpenToPublic && (
          <span>Accueil du public dans la structure : Non</span>
        )}
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
      {isCulturalDomainsEnabled && aboutSection}
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
