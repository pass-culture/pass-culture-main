import type { Story } from '@storybook/react'
import React from 'react'

import BannerWarning, { BannerWarningProps } from './BannerWarning'

export default {
  title: 'ui-kit/BannerWarning',
  component: BannerWarning,
}

const Template: Story<BannerWarningProps> = props => (
  <BannerWarning {...props}>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua.
  </BannerWarning>
)

export const WithoutLink = Template.bind({})
WithoutLink.args = {
  title: 'Without link warning banner',
}

export const WithLink = Template.bind({})
WithLink.args = {
  title: 'With link warning banner',
  links: [
    {
      href: 'https://pro.testing.passculture.team',
      linkTitle: 'Lien vers le pass culture',
    },
  ],
}
