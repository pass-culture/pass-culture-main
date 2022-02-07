import { array, number } from '@storybook/addon-knobs'
import { Story } from '@storybook/react'
import React from 'react'

import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'

import {
  ImportFromComputer,
  ImportFromComputerProps,
} from './ImportFromComputer'

export default {
  title: 'components/ImportFromComputer',
  component: ImportFromComputer,
}

const Template: Story<ImportFromComputerProps> = props => (
  <ImportFromComputer {...props} />
)

export const Portrait = Template.bind({})
Portrait.args = {
  constraints: [
    imageConstraints.formats(array('formats', ['image/jpeg', 'image/png'])),
    imageConstraints.size(number('size', 10_000_000)),
    imageConstraints.width(number('width', 300)),
  ],
  orientation: 'portrait',
  imageTypes: ['image/jpeg', 'image/png'],
  onSetImage: alert,
}

export const Landscape = Template.bind({})
Landscape.args = {
  constraints: [
    imageConstraints.formats(array('formats', ['image/jpeg', 'image/png'])),
    imageConstraints.size(number('size', 10_000_000)),
    imageConstraints.width(number('width', 400)),
  ],
  orientation: 'landscape',
  imageTypes: ['image/jpeg', 'image/png'],
  onSetImage: alert,
}
