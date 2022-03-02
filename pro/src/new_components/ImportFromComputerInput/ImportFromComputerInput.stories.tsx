import { Story } from '@storybook/react'
import React from 'react'

import {
  ImportFromComputerInput,
  IImportFromComputerInputProps,
} from './ImportFromComputerInput'

export default {
  title: 'components/ImportFromComputerInput',
  component: ImportFromComputerInput,
}

const Template: Story<IImportFromComputerInputProps> = props => (
  <ImportFromComputerInput {...props} />
)

export const Default = Template.bind({})
Default.args = {
  isValid: true,
  imageTypes: ['image/jpeg', 'image/png'],
  onSetImage: alert,
}
