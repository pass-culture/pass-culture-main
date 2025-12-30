import type { UseFormSetValue } from 'react-hook-form'

import {
  AccessibilityEnum,
  type AccessibilityFormValues,
} from '@/commons/core/shared/types'
import type { CheckboxGroupProps } from '@/design-system/CheckboxGroup/CheckboxGroup'
import strokeAccessibilityBrainIcon from '@/icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from '@/icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from '@/icons/stroke-accessibility-leg.svg'

export type SetAccessibilityFieldValue = UseFormSetValue<{
  accessibility: AccessibilityFormValues
}>

const DEFAULT_VALUES: AccessibilityFormValues = {
  none: false,
  visual: false,
  mental: false,
  motor: false,
  audio: false,
}

function updateAccessibilityField(
  setFieldValue: SetAccessibilityFieldValue,
  accessibilityValues: Partial<AccessibilityFormValues> | undefined
): CheckboxGroupProps['options'] {
  const onOptionChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    name: AccessibilityEnum
  ) => {
    if (name === AccessibilityEnum.NONE && event.target.checked) {
      setFieldValue(
        'accessibility',
        {
          none: true,
          visual: false,
          mental: false,
          motor: false,
          audio: false,
        },
        {
          shouldValidate: true,
        }
      )

      return
    }

    if (event.target.checked) {
      setFieldValue(
        `accessibility`,
        {
          ...DEFAULT_VALUES,
          ...accessibilityValues,
          [name]: event.target.checked,
          none: false,
        },
        {
          shouldValidate: true,
        }
      )

      return
    }

    setFieldValue(
      `accessibility`,
      {
        ...DEFAULT_VALUES,
        ...accessibilityValues,
        [name]: event.target.checked,
      },
      {
        shouldValidate: true,
      }
    )
  }

  return [
    {
      label: 'Visuel',
      asset: { variant: 'icon', src: strokeAccessibilityEyeIcon },
      sizing: 'fill',
      checked: Boolean(accessibilityValues?.visual),
      onChange: (e) => onOptionChange(e, AccessibilityEnum.VISUAL),
    },
    {
      label: 'Psychique ou cognitif',
      asset: { variant: 'icon', src: strokeAccessibilityBrainIcon },
      sizing: 'fill',
      checked: Boolean(accessibilityValues?.mental),
      onChange: (e) => onOptionChange(e, AccessibilityEnum.MENTAL),
    },
    {
      label: 'Moteur',
      asset: { variant: 'icon', src: strokeAccessibilityLegIcon },
      sizing: 'fill',
      checked: Boolean(accessibilityValues?.motor),
      onChange: (e) => onOptionChange(e, AccessibilityEnum.MOTOR),
    },
    {
      label: 'Auditif',
      asset: { variant: 'icon', src: strokeAccessibilityEarIcon },
      sizing: 'fill',
      checked: Boolean(accessibilityValues?.audio),
      onChange: (e) => onOptionChange(e, AccessibilityEnum.AUDIO),
    },
    {
      label: 'Non accessible',
      sizing: 'fill',
      checked: Boolean(accessibilityValues?.none),
      onChange: (e) => onOptionChange(e, AccessibilityEnum.NONE),
    },
  ]
}

export { updateAccessibilityField }
