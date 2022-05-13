import { ConstraintCheck, ConstraintCheckProps } from './ConstraintCheck'

import React from 'react'
import { Story } from '@storybook/react'
import { imageConstraints } from './imageConstraints'

export default {
  title: 'components/ConstraintCheck',
  component: ConstraintCheck,
}

const Template: Story<ConstraintCheckProps> = props => (
  <ConstraintCheck {...props} />
)

export const Default = Template.bind({})
Default.args = {
  constraints: [
    imageConstraints.formats(['image/png', 'image/jpeg']),
    imageConstraints.size(2_000_000),
    imageConstraints.width(300),
  ],
  failingConstraints: [],
}

export const Failing = Template.bind({})
Failing.args = {
  constraints: [
    imageConstraints.formats(['image/png', 'image/jpeg']),
    imageConstraints.size(2_000_000),
    imageConstraints.width(300),
  ],
  failingConstraints: ['size', 'width'],
}
