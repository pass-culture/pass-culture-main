import { AccessiblityEnum } from 'core/shared'

export const DEFAULT_ACCESSIBILITY_FORM_VALUES = {
  accessibility: {
    [AccessiblityEnum.VISUAL]: false,
    [AccessiblityEnum.MENTAL]: false,
    [AccessiblityEnum.AUDIO]: false,
    [AccessiblityEnum.MOTOR]: false,
    [AccessiblityEnum.NONE]: false,
  },
  isAccessibilityAppliedOnAllOffers: false,
}
