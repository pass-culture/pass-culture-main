import { GetVenueResponseModel } from '@/apiClient/v1'

import { defaultGetVenue } from '../factories/collectiveApiFactories'
import { getAccessibilityInfoFromVenue } from '../getAccessibilityInfoFromVenue'

describe('getAccessibilityInfoFromVenue', () => {
  it('should use venue internal accessibility data when external data is absent', () => {
    const venue: GetVenueResponseModel = {
      ...defaultGetVenue,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
    }

    const accessibilityResult = getAccessibilityInfoFromVenue(venue)

    expect(accessibilityResult.accessibility).toEqual({
      audio: true,
      mental: false,
      motor: true,
      visual: false,
      none: false,
    })
    expect(accessibilityResult.isExternal).toBe(false)
  })

  it('should use venue external accessibility data when external data is present', () => {
    const venue: GetVenueResponseModel = {
      ...defaultGetVenue,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: false,
      externalAccessibilityData: {
        isAccessibleAudioDisability: false,
        isAccessibleMentalDisability: true,
      },
    }

    const accessibilityResult = getAccessibilityInfoFromVenue(venue)

    expect(accessibilityResult.accessibility).toEqual({
      audio: false,
      mental: true,
      motor: true,
      visual: false,
      none: false,
    })
    expect(accessibilityResult.isExternal).toBe(true)
  })

  it('should initialize accessibility data with false values when venue is undefined', () => {
    const venue = undefined

    const accessibilityResult = getAccessibilityInfoFromVenue(venue)

    expect(accessibilityResult.accessibility).toEqual({
      audio: false,
      mental: false,
      motor: false,
      visual: false,
      none: true,
    })
    expect(accessibilityResult.isExternal).toBe(false)
  })
})
