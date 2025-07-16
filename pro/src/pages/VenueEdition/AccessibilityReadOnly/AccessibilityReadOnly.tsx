import { GetVenueResponseModel } from 'apiClient/v1'
import { AccessibilitySummarySection as InternalAccessibilitySummarySection } from 'components/AccessibilitySummarySection/AccessibilitySummarySection'
import { ExternalAccessibility } from 'components/ExternalAccessibility/ExternalAccessibility'
import { SummarySubSubSection } from 'components/SummaryLayout/SummarySubSubSection'

import { AccessibilityCallout } from '../AccessibilityCallout/AccessibilityCallout'

interface AccessibilityReadOnlyProps {
  venue: GetVenueResponseModel
}

export const AccessibilityReadOnly = ({
  venue,
}: AccessibilityReadOnlyProps) => {
  // TODO (igabriele, 2025-07-16): Use `getAccessibilityInfoFromVenue()` common util rather than inlining domain rules.
  if (!venue.externalAccessibilityData) {
    return (
      <InternalAccessibilitySummarySection
        callout={venue.isPermanent ? <AccessibilityCallout /> : null}
        accessibleItem={venue}
        accessibleWording="Votre établissement est accessible aux publics en situation de handicap :"
        shouldShowDivider={false}
        isSubSubSection
      />
    )
  }

  return (
    <SummarySubSubSection title="Modalités d’accessibilité via acceslibre">
      <ExternalAccessibility
        externalAccessibilityId={venue.externalAccessibilityId}
        externalAccessibilityData={venue.externalAccessibilityData}
      />
    </SummarySubSubSection>
  )
}
