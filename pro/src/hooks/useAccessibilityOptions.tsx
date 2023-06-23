import { AccessiblityEnum } from 'core/shared'
import strokeAccessibilityBrain from 'icons/stroke-accessibility-brain.svg'
import audioDisabilitySvg from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEye from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLeg from 'icons/stroke-accessibility-leg.svg'

const useAccessibilityOptions = (
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
      name: `accessibility.${AccessiblityEnum.VISUAL}`,
      icon: strokeAccessibilityEye,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Psychique ou cognitif',
      name: `accessibility.${AccessiblityEnum.MENTAL}`,
      icon: strokeAccessibilityBrain,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Moteur',
      name: `accessibility.${AccessiblityEnum.MOTOR}`,
      icon: strokeAccessibilityLeg,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Auditif',
      name: `accessibility.${AccessiblityEnum.AUDIO}`,
      icon: audioDisabilitySvg,
      onChange: onNormalOptionChange,
    },
    {
      label: 'Non accessible',
      name: `accessibility.${AccessiblityEnum.NONE}`,
      onChange: onNoneOptionChange,
    },
  ]
}

export default useAccessibilityOptions
