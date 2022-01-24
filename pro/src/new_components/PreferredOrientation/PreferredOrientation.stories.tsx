import { Story } from '@storybook/react'
import React from 'react'

import {
  PreferredOrientation,
  PreferredOrientationProps,
} from './PreferredOrientation'

export default {
  title: 'components/PreferredOrientation',
  component: PreferredOrientation,
}

const Template: Story<PreferredOrientationProps> = props => (
  <PreferredOrientation {...props} />
)

export const Portrait = Template.bind({})
Portrait.args = {
  orientation: 'portrait',
}

export const Landscape = Template.bind({})
Landscape.args = {
  orientation: 'landscape',
}
