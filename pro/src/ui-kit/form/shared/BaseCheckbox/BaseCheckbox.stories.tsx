import type { StoryObj } from '@storybook/react'

import strokeAccessibilityEye from 'icons/stroke-accessibility-eye.svg'

import { BaseCheckbox, CheckboxVariant } from './BaseCheckbox'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

export const Default: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox Label',
    icon: strokeAccessibilityEye,
  },
}

export const WithPartialCheck: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox Label',
    icon: strokeAccessibilityEye,
    partialCheck: true,
  },
}

export const WithBorder: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox Label with border',
    icon: strokeAccessibilityEye,
    variant: CheckboxVariant.BOX,
  },
}
