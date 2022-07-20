import { AccessiblityEnum } from 'core/shared'
import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'

export const accessibilityOptions = [
  {
    label: 'Visuel',
    name: `accessibility.${AccessiblityEnum.VISUAL}`,
    icon: VisualDisabilitySvg,
  },
  {
    label: 'Psychique ou cognitif',
    name: `accessibility.${AccessiblityEnum.MENTAL}`,
    icon: MentalDisabilitySvg,
  },
  {
    label: 'Moteur',
    name: `accessibility.${AccessiblityEnum.MOTOR}`,
    icon: MotorDisabilitySvg,
  },
  {
    label: 'Auditif',
    name: `accessibility.${AccessiblityEnum.AUDIO}`,
    icon: AudioDisabilitySvg,
  },
  { label: 'Non accessible', name: `accessibility.${AccessiblityEnum.NONE}` },
]
