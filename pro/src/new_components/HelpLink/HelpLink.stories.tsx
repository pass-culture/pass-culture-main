import HelpLink from './HelpLink'
import React from 'react'
import { Story } from '@storybook/react'

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
