import Hero from './Hero'
import { MemoryRouter } from 'react-router-dom'
import React from 'react'

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
