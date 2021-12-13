import { Story } from '@storybook/react'
import React from 'react'

import { BaseInput } from '../'

import FieldGroup from './FieldGroup'

export default {
  title: 'ui-kit/forms/shared/FieldGroup',
  component: FieldGroup,
}

const Template: Story<{
  className: string
}> = args => (
  <FieldGroup {...args}>
    <BaseInput type="text" />
    <BaseInput placeholder="Rechercher le terme" type="text" />
  </FieldGroup>
)

export const Default = Template.bind({})

Default.args = {
  className: 'string',
}
