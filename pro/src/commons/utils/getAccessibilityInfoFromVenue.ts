import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'

export function getAccessibilityInfoFromVenue(
  venue: GetVenueResponseModel | VenueListItemResponseModel | undefined
): {
  accessibility: AccessibilityFormValues
  isExternal: boolean
} {
  if (!venue) {
    return {
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        visual: false,
        none: true,
      },
      isExternal: false,
    }
  }

  if (!venue.externalAccessibilityData) {
    return {
      accessibility: {
        audio: !!venue.audioDisabilityCompliant,
        mental: !!venue.mentalDisabilityCompliant,
        motor: !!venue.motorDisabilityCompliant,
        visual: !!venue.visualDisabilityCompliant,
        none: false,
      },
      isExternal: false,
    }
  }

  return {
    accessibility: {
      audio:
        venue.externalAccessibilityData.isAccessibleAudioDisability ??
        !!venue.audioDisabilityCompliant,
      mental:
        venue.externalAccessibilityData.isAccessibleMentalDisability ??
        !!venue.mentalDisabilityCompliant,
      motor:
        venue.externalAccessibilityData.isAccessibleMotorDisability ??
        !!venue.motorDisabilityCompliant,
      visual:
        venue.externalAccessibilityData.isAccessibleVisualDisability ??
        !!venue.visualDisabilityCompliant,
      none: false,
    },
    isExternal: true,
  }
}
