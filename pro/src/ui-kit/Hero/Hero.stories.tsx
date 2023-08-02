import { Story } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import Hero, { HeroProps } from './Hero'

export default {
  title: 'components/Hero',
  component: Hero,
  decorators: [withRouter],
}
const Template: Story<HeroProps> = args => <Hero {...args} />

export const Default = Template.bind({})

Default.args = {
  title: 'Mon titre',
  text: 'Une petite explication',
  linkLabel: 'cliquez-moi !',
  linkTo: '/',
}
