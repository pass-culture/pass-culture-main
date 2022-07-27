import type { Story } from '@storybook/react'
import React from 'react'

import BaseRadio from './BaseRadio'

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
