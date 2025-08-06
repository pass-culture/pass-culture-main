import type { StoryObj } from '@storybook/react'

import { Callout } from './Callout'

export default {
  title: '@/ui-kit/Callout',
  component: Callout,
}

export const WithoutLink: StoryObj<typeof Callout> = {
  args: {
    children:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'Without link warning callout',
  },
}

export const Closable: StoryObj<typeof Callout> = {
  args: {
    children:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'Without link warning callout',
    closable: true,
  },
}

export const WithLink: StoryObj<typeof Callout> = {
  args: {
    children:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
    title: 'With link warning callout',
    links: [
      {
        href: 'https://pro.testing.passculture.team',
        label: 'Lien interne au pass culture pro',
        isExternal: true,
      },
      {
        href: 'https://pro.testing.passculture.team',
        label: 'Lien externe',
        isExternal: true,
      },
    ],
  },
}
