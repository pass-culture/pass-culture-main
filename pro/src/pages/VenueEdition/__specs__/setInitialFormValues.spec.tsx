import { AccessibilityEnum } from 'core/shared/types'
import { defaultGetVenue } from 'utils/collectiveApiFactories'

import { buildAccessibilityFormValues } from '../setInitialFormValues'

describe('buildAccessibilityFormValues', () => {
  it('should return false if venue and access libre values are not defined', () => {
    expect(
      buildAccessibilityFormValues({
        ...defaultGetVenue,
        audioDisabilityCompliant: null,
        mentalDisabilityCompliant: null,
        motorDisabilityCompliant: null,
        visualDisabilityCompliant: null,
        externalAccessibilityData: null,
      })
    ).toEqual({
      [AccessibilityEnum.AUDIO]: false,
      [AccessibilityEnum.MENTAL]: false,
      [AccessibilityEnum.MOTOR]: false,
      [AccessibilityEnum.VISUAL]: false,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should return the venue values if they are defined', () => {
    expect(
      buildAccessibilityFormValues({
        ...defaultGetVenue,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        externalAccessibilityData: null,
      })
    ).toEqual({
      [AccessibilityEnum.AUDIO]: true,
      [AccessibilityEnum.MENTAL]: true,
      [AccessibilityEnum.MOTOR]: true,
      [AccessibilityEnum.VISUAL]: true,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should return the acces libre values if they are defined', () => {
    expect(
      buildAccessibilityFormValues({
        ...defaultGetVenue,
        audioDisabilityCompliant: null,
        mentalDisabilityCompliant: null,
        motorDisabilityCompliant: null,
        visualDisabilityCompliant: null,
        externalAccessibilityData: {
          isAccessibleAudioDisability: true,
          isAccessibleMotorDisability: true,
          isAccessibleMentalDisability: true,
          isAccessibleVisualDisability: true,
        },
      })
    ).toEqual({
      [AccessibilityEnum.AUDIO]: true,
      [AccessibilityEnum.MENTAL]: true,
      [AccessibilityEnum.MOTOR]: true,
      [AccessibilityEnum.VISUAL]: true,
      [AccessibilityEnum.NONE]: false,
    })
  })

  it('should prioritize acces libre values over venue values', () => {
    expect(
      buildAccessibilityFormValues({
        ...defaultGetVenue,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
        externalAccessibilityData: {
          isAccessibleAudioDisability: false,
          isAccessibleMotorDisability: false,
          isAccessibleMentalDisability: false,
          isAccessibleVisualDisability: false,
        },
      })
    ).toEqual({
      [AccessibilityEnum.AUDIO]: false,
      [AccessibilityEnum.MENTAL]: false,
      [AccessibilityEnum.MOTOR]: false,
      [AccessibilityEnum.VISUAL]: false,
      [AccessibilityEnum.NONE]: true,
    })
  })
})
