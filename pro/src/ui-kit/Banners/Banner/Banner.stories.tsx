import type { StoryObj } from '@storybook/react'

import { Banner } from './Banner'

export default {
  title: 'ui-kit/Banner',
  component: Banner,
}

const textMock =
  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'

export const Attention: StoryObj<typeof Banner> = {
  args: {
    type: 'attention',
    children: textMock,
  },
}

export const AttentionWithoutTitle: StoryObj<typeof Banner> = {
  args: {
    type: 'attention',
    showTitle: false,
    children: textMock,
  },
}

export const Info: StoryObj<typeof Banner> = {
  args: {
    type: 'notification-info',
    children: textMock,
  },
}

export const InfoWithoutTitle: StoryObj<typeof Banner> = {
  args: {
    type: 'notification-info',
    showTitle: false,
    children: textMock,
  },
}

export const Light: StoryObj<typeof Banner> = {
  args: {
    type: 'light',
    children: textMock,
  },
}
export const Minimal: StoryObj<typeof Banner> = {
  args: {
    minimalStyle: true,
    children: textMock,
  },
}

export const WithLink: StoryObj<typeof Banner> = {
  args: {
    links: [
      {
        href: 'https://pro.testing.passculture.team',
        label: 'Lien vers le pass culture',
        isExternal: true,
      },
      {
        href: '#',
        label: 'Un autre lien',
        isExternal: true,
      },
    ],
    minimalStyle: false,
    type: 'notification-info',
  },
}
