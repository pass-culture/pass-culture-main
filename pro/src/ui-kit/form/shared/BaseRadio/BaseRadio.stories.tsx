import BaseRadio from './BaseRadio'
import React from 'react'
import { Story } from '@storybook/react'

export default {
  title: 'ui-kit/forms/shared/BaseRadio',
  component: BaseRadio,
}

const Template: Story<{
  label: string
  hasError: boolean
  disabled: boolean
  checked: boolean
}> = args => (
  <div>
    <BaseRadio {...args} />
  </div>
)

export const Default = Template.bind({})

Default.args = {
  label: 'radio label',
  hasError: false,
  disabled: false,
  checked: false,
}
