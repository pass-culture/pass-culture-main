import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'

export function getAccessibilityInfoFromVenue(
  venue: GetVenueResponseModel | VenueListItemResponseModel | undefined
): {
  accessibility: AccessibilityFormValues
  isExternal: boolean
} {
  const baseAccessibility = venue?.externalAccessibilityData
    ? {
        audio: !!venue.externalAccessibilityData.isAccessibleAudioDisability,
        mental: !!venue.externalAccessibilityData.isAccessibleMentalDisability,
        motor: !!venue.externalAccessibilityData.isAccessibleMotorDisability,
        visual: !!venue.externalAccessibilityData.isAccessibleVisualDisability,
      }
    : {
        audio: !!venue?.audioDisabilityCompliant,
        mental: !!venue?.mentalDisabilityCompliant,
        motor: !!venue?.motorDisabilityCompliant,
        visual: !!venue?.visualDisabilityCompliant,
      }
  const hasSomeAccessibility = Object.values(baseAccessibility).some((v) => v)
  const isExternal = !!venue?.externalAccessibilityData

  return {
    accessibility: {
      ...baseAccessibility,
      none: !hasSomeAccessibility,
    },
    isExternal,
  }
}
