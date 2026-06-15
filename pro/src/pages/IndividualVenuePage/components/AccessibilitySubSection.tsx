import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { AccessibilitySummarySection as InternalAccessibilitySummarySection } from '@/components/AccessibilitySummarySection/AccessibilitySummarySection'
import { ExternalAccessibility } from '@/components/ExternalAccessibility/ExternalAccessibility'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { AccessibilityCallout } from './AccessibilityCallout'

export const AccessibilitySubSection = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  // TODO (igabriele, 2025-07-16): Use `getAccessibilityInfoFromVenue()` common util rather than inlining domain rules.
  if (!selectedPartnerVenue.externalAccessibilityData) {
    return (
      <InternalAccessibilitySummarySection
        callout={
          selectedPartnerVenue.isPermanent ? <AccessibilityCallout /> : null
        }
        accessibleItem={selectedPartnerVenue}
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
        externalAccessibilityId={selectedPartnerVenue.externalAccessibilityId}
        externalAccessibilityData={
          selectedPartnerVenue.externalAccessibilityData
        }
      />
    </SummarySubSection>
  )
}
