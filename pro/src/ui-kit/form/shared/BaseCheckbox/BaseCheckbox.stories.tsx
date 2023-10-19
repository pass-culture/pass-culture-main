import type { Story } from '@storybook/react'
import React from 'react'

import strokeAccessibilityEye from 'icons/stroke-accessibility-eye.svg'

import BaseCheckbox, { BaseCheckboxProps } from './BaseCheckbox'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

const Template: Story<BaseCheckboxProps> = (args) => (
  <div>
    <BaseCheckbox {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  label: 'Checkbox Label',
  hasError: false,
  disabled: false,
  onChange: () => {},
  icon: strokeAccessibilityEye,
}

export const WithPartialCheck = Template.bind({})

WithPartialCheck.args = {
  label: 'Checkbox Label',
  hasError: false,
  disabled: false,
  onChange: () => {},
  icon: strokeAccessibilityEye,
  partialCheck: true,
}

export const WithBorder = Template.bind({})

WithBorder.args = {
  label: 'Checkbox Label with border',
  hasError: false,
  disabled: false,
  onChange: () => {},
  icon: strokeAccessibilityEye,
  withBorder: true,
}
