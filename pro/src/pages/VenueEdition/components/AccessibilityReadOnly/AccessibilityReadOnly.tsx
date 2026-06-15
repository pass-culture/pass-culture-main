import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { AccessibilitySummarySection as InternalAccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { ExternalAccessibility } from '@/components/ExternalAccessibility/ExternalAccessibility'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

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
    <SummarySubSection
      title="Modalités d’accessibilité via acceslibre"
      shouldShowDivider={false}
    >
      <ExternalAccessibility
        externalAccessibilityId={venue.externalAccessibilityId}
        externalAccessibilityData={venue.externalAccessibilityData}
      />
    </SummarySubSection>
  )
}
