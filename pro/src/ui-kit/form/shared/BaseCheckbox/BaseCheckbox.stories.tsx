import type { StoryObj } from '@storybook/react'

import strokeAccessibilityEyeIcon from 'icons/stroke-accessibility-eye.svg'

import { BaseCheckbox, CheckboxVariant } from './BaseCheckbox'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

export const Default: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox label',
    icon: strokeAccessibilityEyeIcon,
  },
}

export const Checked: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox checked',
    checked: true,
    onChange: () => {},
  },
}

export const Disabled: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox checked',
    checked: true,
    disabled: true,
    onChange: () => {},
  },
}

export const PartialCheck: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox with partial check',
    partialCheck: true,
  },
}

export const Box: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox with border',
    variant: CheckboxVariant.BOX,
    checked: true,
    onChange: () => {},
  },
}

export const BoxWithChildren: StoryObj<typeof BaseCheckbox> = {
  args: {
    label: 'Checkbox with border and children',
    variant: CheckboxVariant.BOX,
    checked: true,
    childrenOnChecked: <span>Child content</span>,
    onChange: () => {},
  },
}
