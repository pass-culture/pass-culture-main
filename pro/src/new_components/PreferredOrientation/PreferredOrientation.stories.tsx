import {
  IPreferredOrientationProps,
  PreferredOrientation,
} from './PreferredOrientation'

import React from 'react'
import { Story } from '@storybook/react'

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
