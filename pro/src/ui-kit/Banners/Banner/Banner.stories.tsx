import type { Story } from '@storybook/react'
import React from 'react'

import Banner, { IBannerProps } from './Banner'

export default {
  title: 'ui-kit/Banner',
  component: Banner,
}

const Template: Story<IBannerProps> = props => (
  <Banner {...props}>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua.
  </Banner>
)

export const Attention = Template.bind({})
Attention.args = { type: 'attention', closable: true }

export const Info = Template.bind({})
Info.args = { type: 'notification-info', closable: true }

export const Light = Template.bind({})
Light.args = { type: 'light', closable: true }

export const WithLink = Template.bind({})
WithLink.args = {
  links: [
    {
      href: 'https://pro.testing.passculture.team',
      linkTitle: 'Lien vers le pass culture',
    },
    {
      href: '#',
      linkTitle: 'Un autre lien',
    },
  ],
  closable: false,
  type: 'notification-info',
}
