import { GetVenueResponseModel } from 'apiClient/v1'
import { AccessibilitySummarySection as InternalAccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { ExternalAccessibility } from 'components/ExternalAccessibility/ExternalAccessibility'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { SummarySubSubSection } from 'components/SummaryLayout/SummarySubSubSection'

import { AccessibilityCallout } from '../AccessibilityCallout/AccessibilityCallout'

interface AccessibilityReadOnlyProps {
  isOpenToPublicEnabled: boolean
  venue: GetVenueResponseModel
}

export const AccessibilityReadOnly = ({ isOpenToPublicEnabled, venue }: AccessibilityReadOnlyProps) => {
  const isSubSubSection = isOpenToPublicEnabled

  if (!venue.externalAccessibilityData) {
    return <InternalAccessibilitySummarySection
      callout={
        venue.isPermanent ? (
          <AccessibilityCallout />
        ) : null
      }
      accessibleItem={venue}
      accessibleWording="Votre établissement est accessible aux publics en situation de handicap :"
      shouldShowDivider={false}
      isSubSubSection={isSubSubSection}
    />
  }

  const sectionContent = <ExternalAccessibility
    externalAccessibilityId={venue.externalAccessibilityId}
    externalAccessibilityData={venue.externalAccessibilityData}
  />

  return isSubSubSection ? (
    <SummarySubSubSection title="Modalités d’accessibilité via acceslibre">
      {sectionContent}
    </SummarySubSubSection>
  ) : (
    <SummarySubSection title="Modalités d’accessibilité via acceslibre" shouldShowDivider={false}>
      {sectionContent}
    </SummarySubSection>
  )
}