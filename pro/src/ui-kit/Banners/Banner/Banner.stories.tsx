import type { Story } from '@storybook/react'
import React from 'react'

import BannerImage from './assets/job_highlights_banner.svg'
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

const ImageTemplate: Story<IBannerProps> = props => (
  <Banner {...props}>
    <a
      href="https://docsend.com/view/n9yniyrtusp82a9m"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="en savoir plus sur les temps fort des métiers de la culture"
    >
      <BannerImage />
    </a>
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

export const Image = ImageTemplate.bind({})
Image.args = { type: 'image', closable: true }

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
