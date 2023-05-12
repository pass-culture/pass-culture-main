import type { Story } from '@storybook/react'
import React from 'react'

import Divider, { DividerProps } from './Divider'

export default {
  title: 'ui-kit/Divider',
  component: Divider,
}

const Template: Story<DividerProps> = args => (
  <div>
    <p>Second text</p>
    <Divider {...args} />
    <p>Second text</p>
  </div>
)

export const Default = Template.bind({})
Default.args = {
  size: 'medium',
}
