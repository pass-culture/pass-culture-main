import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import Hero from './Hero'

export default {
  title: 'components/Hero',
  component: Hero,
  decorators: [
    Story => (
      <MemoryRouter>
        <Story />
      </MemoryRouter>
    ),
  ],
}
const Template = args => <Hero {...args} />

export const Default = Template.bind({})

Default.args = {
  title: 'Mon titre',
  text: 'Une petite explication',
  linkLabel: 'cliquez-moi !',
  linkTo: '/',
}
