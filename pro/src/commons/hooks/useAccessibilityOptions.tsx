import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { AccessibilityEnum } from 'commons/core/shared/types'
import strokeAccessibilityBrainIcon from 'icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from 'icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from 'icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from 'icons/stroke-accessibility-leg.svg'
import { CheckboxGroupProps } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'

export const useAccessibilityOptions = (
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => void,
  accessibilityValues: OfferEducationalFormValues['accessibility']
) => {
  const onNoneOptionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setFieldValue('accessibility', {
        none: true,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      })
    } else {
      setFieldValue('accessibility.none', false)
    }
  }
  const onNormalOptionChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    name: AccessibilityEnum
  ) => {
    if (event.target.checked) {
      setFieldValue(`accessibility.none`, false)
    }

    setFieldValue(`accessibility.${name}`, event.target.checked)
  }
  return [
    {
      label: 'Visuel',
      icon: strokeAccessibilityEyeIcon,
      sizing: 'fill',
      checked: accessibilityValues.visual,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        onNormalOptionChange(e, AccessibilityEnum.VISUAL),
    },
    {
      label: 'Psychique ou cognitif',
      icon: strokeAccessibilityBrainIcon,
      sizing: 'fill',
      checked: accessibilityValues.mental,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        onNormalOptionChange(e, AccessibilityEnum.MENTAL),
    },
    {
      label: 'Moteur',
      icon: strokeAccessibilityLegIcon,
      sizing: 'fill',
      checked: accessibilityValues.motor,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        onNormalOptionChange(e, AccessibilityEnum.MOTOR),
    },
    {
      label: 'Auditif',
      icon: strokeAccessibilityEarIcon,
      sizing: 'fill',
      checked: accessibilityValues.audio,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        onNormalOptionChange(e, AccessibilityEnum.AUDIO),
    },
    {
      label: 'Non accessible',
      sizing: 'fill',
      checked: accessibilityValues.none,
      onChange: onNoneOptionChange,
    },
  ] satisfies CheckboxGroupProps['group']
}
