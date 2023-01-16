import type { ComponentStory } from '@storybook/react'
import React from 'react'

import BaseRadio from './BaseRadio'

export default {
  title: 'ui-kit/forms/shared/BaseRadio',
  component: BaseRadio,
}

const Template: ComponentStory<typeof BaseRadio> = args => (
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

export const WithBorder = Template.bind({})

WithBorder.args = {
  label: 'radio label',
  hasError: false,
  disabled: false,
  checked: false,
  withBorder: true,
}
