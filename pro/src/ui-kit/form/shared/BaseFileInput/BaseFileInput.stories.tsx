import type { Story } from '@storybook/react'
import React from 'react'

import BaseFileInput, { BaseFileInputProps } from './BaseFileInput'

export default {
  title: 'ui-kit/forms/shared/FileInput',
  component: BaseFileInput,
}

const Template: Story<BaseFileInputProps> = (props) => (
  <BaseFileInput {...props} />
)

export const Default = Template.bind({})
Default.args = {
  label: 'Importer une image depuis l’ordinateur',
  isValid: true,
  fileTypes: ['image/jpeg', 'image/png'],
  onChange: alert,
}
