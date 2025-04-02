import { AccessibilityEnum } from 'commons/core/shared/types'
import strokeAccessibilityBrainIcon from 'icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from 'icons/stroke-accessibility-leg.svg'

export const useAccessibilityOptions = (
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => void,
  groupeName = 'accessibility'
) => {
  const onNoneOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setFieldValue(groupeName, {
        none: true,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      })
      return
    }
    setFieldValue('accessibility.none', false)
  }
  const onNormalOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFieldValue('accessibility.none', false)
    setFieldValue(event.target.name, event.target.checked)
  }
  return [
    {
      label: 'Visuel',
      name: `accessibility.${AccessibilityEnum.VISUAL}`,
      icon: strokeAccessibilityEyeIcon,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Psychique ou cognitif',
      name: `accessibility.${AccessibilityEnum.MENTAL}`,
      icon: strokeAccessibilityBrainIcon,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Moteur',
      name: `accessibility.${AccessibilityEnum.MOTOR}`,
      icon: strokeAccessibilityLegIcon,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Auditif',
      name: `accessibility.${AccessibilityEnum.AUDIO}`,
      icon: strokeAccessibilityEarIcon,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Non accessible',
      name: `accessibility.${AccessibilityEnum.NONE}`,
      onChange: onNoneOptionChange,
    },
  ]
}
