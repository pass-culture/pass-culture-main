import { Story } from '@storybook/react'
import React from 'react'

import {
  IPreferredOrientationProps,
  PreferredOrientation,
} from './PreferredOrientation'

export default {
  title: 'components/PreferredOrientation',
  component: PreferredOrientation,
}

const Template: Story<IPreferredOrientationProps> = props => (
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
