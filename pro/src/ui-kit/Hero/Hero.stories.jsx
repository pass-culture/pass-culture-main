import React from 'react'

import { withRouterDecorator } from 'stories/decorators/withRouter'

import Hero from './Hero'

export default {
  title: 'components/Hero',
  component: Hero,
  decorators: [withRouterDecorator],
}
const Template = args => <Hero {...args} />

export const Default = Template.bind({})

Default.args = {
  title: 'Mon titre',
  text: 'Une petite explication',
  linkLabel: 'cliquez-moi !',
  linkTo: '/',
}
