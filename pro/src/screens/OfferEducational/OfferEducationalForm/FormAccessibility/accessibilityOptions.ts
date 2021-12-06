import { ACCESSIBILITY } from 'core/OfferEducational'
import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'

export const accessibilityOptions = [
  {
    label: 'Visuel',
    name: `accessibility.${ACCESSIBILITY.VISUAL}`,
    icon: VisualDisabilitySvg,
  },
  {
    label: 'Psychique ou cognitif',
    name: `accessibility.${ACCESSIBILITY.MENTAL}`,
    icon: MentalDisabilitySvg,
  },
  {
    label: 'Moteur',
    name: `accessibility.${ACCESSIBILITY.MOTOR}`,
    icon: MotorDisabilitySvg,
  },
  {
    label: 'Auditif',
    name: `accessibility.${ACCESSIBILITY.AUDIO}`,
    icon: AudioDisabilitySvg,
  },
  { label: 'Non accessible', name: `accessibility.${ACCESSIBILITY.NONE}` },
]
