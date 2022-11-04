import { AccessiblityEnum } from 'core/shared'

export const ACCESSIBILITY_DEFAULT_VALUES = {
  accessibility: {
    [AccessiblityEnum.VISUAL]: false,
    [AccessiblityEnum.MENTAL]: false,
    [AccessiblityEnum.AUDIO]: false,
    [AccessiblityEnum.MOTOR]: false,
    [AccessiblityEnum.NONE]: false,
  },
}
