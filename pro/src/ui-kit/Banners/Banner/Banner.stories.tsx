import type { Story } from '@storybook/react'
import React from 'react'

import Banner, { BannerProps } from './Banner'

export default {
  title: 'ui-kit/Banner',
  component: Banner,
}

const Template: Story<BannerProps> = props => (
  <Banner {...props}>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua.
  </Banner>
)

export const Attention = Template.bind({})
Attention.args = { type: 'attention', closable: true }

export const AttentionWithoutTitle = Template.bind({})
AttentionWithoutTitle.args = { type: 'attention', showTitle: false }

export const Info = Template.bind({})
Info.args = { type: 'notification-info', closable: true }

export const InfoWithoutTitle = Template.bind({})
InfoWithoutTitle.args = { type: 'notification-info', showTitle: false }

export const Light = Template.bind({})
Light.args = { type: 'light', closable: true }

export const Minimal = Template.bind({})
Minimal.args = { minimalStyle: true }

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
  minimalStyle: false,
  closable: false,
  type: 'notification-info',
}
