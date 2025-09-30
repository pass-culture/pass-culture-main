import type { UseFormSetValue } from 'react-hook-form'

import {
  AccessibilityEnum,
  type AccessibilityFormValues,
} from '@/commons/core/shared/types'
import type { CheckboxGroupOption } from '@/design-system/CheckboxGroup/CheckboxGroup'
import strokeAccessibilityBrainIcon from '@/icons/stroke-accessibility-brain.svg'
import strokeAccessibilityEarIcon from '@/icons/stroke-accessibility-ear.svg'
import strokeAccessibilityEyeIcon from '@/icons/stroke-accessibility-eye.svg'
import strokeAccessibilityLegIcon from '@/icons/stroke-accessibility-leg.svg'

type SetFieldValue =
  | ((field: string, value: AccessibilityFormValues) => void)
  | UseFormSetValue<{ accessibility: AccessibilityFormValues }>

type AccessibilityOptions = {
  options: CheckboxGroupOption[]
  onChange: (value: string[]) => void
  toCheckboxGroupValues: (
    accessibilityValues?: AccessibilityFormValues
  ) => string[]
}

function useAccessibilityOptions(
  setFieldValue: SetFieldValue
): AccessibilityOptions {
  const onChange = (values: string[]) => {
    if (values.at(-1) === AccessibilityEnum.NONE) {
      setFieldValue('accessibility', {
        none: true,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      })
    } else {
      const accessibilityValues = Object.values(AccessibilityEnum)
        .filter((value) => value !== AccessibilityEnum.NONE)
        .reduce(
          (acc, value) => {
            acc[value as keyof AccessibilityFormValues] = values.includes(value)
            return acc
          },
          { none: false } as AccessibilityFormValues
        )
      setFieldValue(`accessibility`, accessibilityValues)
    }
  }

  const options = [
    {
      label: 'Visuel',
      name: 'accessibility',
      value: AccessibilityEnum.VISUAL,
      variant: 'detailed',
      asset: { variant: 'icon', src: strokeAccessibilityEyeIcon },
      sizing: 'fill',
    },
    {
      label: 'Psychique ou cognitif',
      name: 'accessibility',
      value: AccessibilityEnum.MENTAL,
      variant: 'detailed',
      asset: { variant: 'icon', src: strokeAccessibilityBrainIcon },
      sizing: 'fill',
    },
    {
      label: 'Moteur',
      name: 'accessibility',
      value: AccessibilityEnum.MOTOR,
      variant: 'detailed',
      asset: { variant: 'icon', src: strokeAccessibilityLegIcon },
      sizing: 'fill',
    },
    {
      label: 'Auditif',
      name: 'accessibility',
      value: AccessibilityEnum.AUDIO,
      variant: 'detailed',
      asset: { variant: 'icon', src: strokeAccessibilityEarIcon },
      sizing: 'fill',
    },
    {
      label: 'Non accessible',
      name: 'accessibility',
      value: AccessibilityEnum.NONE,
      variant: 'detailed',
      sizing: 'fill',
    },
  ] satisfies CheckboxGroupOption[]

  const toCheckboxGroupValues = (
    accessibilityValues?: AccessibilityFormValues
  ) => {
    return Object.entries(accessibilityValues || {})
      .filter(([, value]) => value)
      .map(([key]) => key)
  }

  return {
    options,
    onChange,
    toCheckboxGroupValues,
  }
}

export { useAccessibilityOptions }
