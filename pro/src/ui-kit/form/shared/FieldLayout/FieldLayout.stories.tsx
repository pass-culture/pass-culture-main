import { BaseInput } from '../'
import FieldLayout from './FieldLayout'
import React from 'react'
import { Story } from '@storybook/react'

export default {
  title: 'ui-kit/forms/shared/FieldLayout',
  component: FieldLayout,
}

const Template: Story<{
  label: string
  name: string
  className: string
  showError: boolean
  error: string
  count: number
  maxLength: number
  isOptional: boolean
}> = args => (
  <FieldLayout {...args}>
    <BaseInput type="text" />
  </FieldLayout>
)

export const Default = Template.bind({})

Default.args = {
  label: 'Votre numéro de téléphone',
  name: 'string',
  className: 'string',
  showError: true,
  error: 'error message',
  count: 10,
  maxLength: 100,
  isOptional: true,
}
