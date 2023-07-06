import type { Story } from '@storybook/react'
import React from 'react'

import strokeCalendarIcon from 'icons/stroke-calendar.svg'

import BaseInput, { BaseInputProps } from './BaseInput'

export default {
  title: 'ui-kit/forms/shared/BaseInput',
  component: BaseInput,
}

const Template: Story<BaseInputProps> = args => (
  <div>
    <BaseInput {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  hasError: false,
  rightIcon: strokeCalendarIcon,
}
