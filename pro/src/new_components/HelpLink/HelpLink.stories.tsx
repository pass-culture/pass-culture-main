import { Story } from '@storybook/react'
import React from 'react'

import HelpLink from './HelpLink'

export default {
  title: 'components/HelpLink',
  component: HelpLink,
}
const Template: Story = args => (
  <div style={{ width: 500, height: 500 }}>
    <HelpLink {...args} />
  </div>
)

export const Default = Template.bind({})
