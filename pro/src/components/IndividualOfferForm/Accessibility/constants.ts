import { AccessibilityEnum } from 'core/shared/types'

export const ACCESSIBILITY_DEFAULT_VALUES = {
  accessibility: {
    [AccessibilityEnum.VISUAL]: false,
    [AccessibilityEnum.MENTAL]: false,
    [AccessibilityEnum.AUDIO]: false,
    [AccessibilityEnum.MOTOR]: false,
    [AccessibilityEnum.NONE]: false,
  },
}
