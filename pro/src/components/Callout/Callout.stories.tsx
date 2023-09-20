import type { Story } from '@storybook/react'
import React from 'react'

import Callout, { CalloutProps } from './Callout'

export default {
  title: 'components/Callout',
  component: Callout,
}

const Template: Story<CalloutProps> = props => (
  <Callout {...props}>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua.
  </Callout>
)

export const WithoutLink = Template.bind({})
WithoutLink.args = {
  title: 'Without link warning callout',
}
export const Closable = Template.bind({})
WithoutLink.args = {
  title: 'Without link warning callout',
  closable: true,
}

export const WithLink = Template.bind({})
WithLink.args = {
  title: 'With link warning callout',
  links: [
    {
      href: 'https://pro.testing.passculture.team',
      linkTitle: 'Lien vers le pass culture',
    },
    {
      href: 'https://pro.testing.passculture.team',
      linkTitle: 'Lien vers autre chose',
    },
  ],
}
