import { GetVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { AccessibilitySummarySection as InternalAccessibilitySummarySubSection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { ExternalAccessibility } from 'components/ExternalAccessibility/ExternalAccessibility'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { OpeningHoursReadOnly } from 'pages/VenueEdition/OpeningHoursReadOnly/OpeningHoursReadOnly'

import { AccessibilityCallout } from './AccessibilityCallout/AccessibilityCallout'

interface VenueEditionReadOnlyProps {
  venue: GetVenueResponseModel
}

export const VenueEditionReadOnly = ({ venue }: VenueEditionReadOnlyProps) => {
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')
  const isVenueOpenToPublic = !!venue.isOpenToPublic
  const isAccessibilitySectionDisplayed = isOpenToPublicEnabled ? isVenueOpenToPublic : true

  return (
    <SummarySection
      title="Vos informations pour le grand public"
      editLink={`/structures/${venue.managingOfferer.id}/lieux/${venue.id}/edition`}
    >
      <SummarySubSection
        title="À propos de votre activité"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Description',
              text: venue.description ?? 'Non renseignée',
            },
          ]}
        />
      </SummarySubSection>
      <OpeningHoursReadOnly
        isOpenToPublicEnabled={isOpenToPublicEnabled}
        isOpenToPublic={isVenueOpenToPublic}
        openingHours={venue.openingHours}
      />
      {isAccessibilitySectionDisplayed && (
        venue.externalAccessibilityData ? (
          <>
            <SummarySubSection
              title="Modalités d’accessibilité via acceslibre"
              shouldShowDivider={false}
            >
              <ExternalAccessibility
                externalAccessibilityId={venue.externalAccessibilityId}
                externalAccessibilityData={venue.externalAccessibilityData}
              />
            </SummarySubSection>
          </>
        ): (
          <InternalAccessibilitySummarySubSection
            callout={
              venue.isPermanent ? (
                <AccessibilityCallout />
              ) : null
            }
            accessibleItem={venue}
            accessibleWording="Votre établissement est accessible aux publics en situation de handicap :"
            shouldShowDivider={false}
          />
        )
      )}
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
