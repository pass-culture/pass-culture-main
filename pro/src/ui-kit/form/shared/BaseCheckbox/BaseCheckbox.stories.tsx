import type { Story } from '@storybook/react'
import React from 'react'

import icon from 'icons/visual-disability.svg'

import BaseCheckbox, { BaseCheckboxProps } from './BaseCheckbox'

export default {
  title: 'ui-kit/forms/shared/BaseCheckbox',
  component: BaseCheckbox,
}

const Template: Story<BaseCheckboxProps> = args => (
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
  icon,
}

export const WithDescription = Template.bind({})

WithDescription.args = {
  label: 'Checkbox Label',
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
  hasError: false,
  disabled: false,
  onChange: () => {},
  icon,
}

export const WithBorder = Template.bind({})

WithBorder.args = {
  label: 'Checkbox Label with border',
  hasError: false,
  disabled: false,
  onChange: () => {},
  icon,
  withBorder: true,
}
