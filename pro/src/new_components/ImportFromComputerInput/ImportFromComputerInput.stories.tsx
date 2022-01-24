import { Story } from '@storybook/react'
import React from 'react'

import {
  ImportFromComputerInput,
  ImportFromComputerInputProps,
} from './ImportFromComputerInput'

export default {
  title: 'components/ImportFromComputerInput',
  component: ImportFromComputerInput,
}

const Template: Story<ImportFromComputerInputProps> = props => (
  <ImportFromComputerInput {...props} />
)

export const Default = Template.bind({})
Default.args = {
  isValid: true,
  imageTypes: ['image/jpeg', 'image/png'],
  onSetImage: alert,
}
