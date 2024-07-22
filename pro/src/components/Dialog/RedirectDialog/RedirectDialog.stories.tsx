import type { StoryObj } from '@storybook/react'

import { RedirectDialog } from './RedirectDialog'

export default {
  title: 'components/Dialog/RedirectDialog',
  component: RedirectDialog,
}

export const Default: StoryObj<typeof RedirectDialog> = {
  args: {
    title: 'title',
    redirectText: 'Go to ...',
    redirectLink: {
      to: 'https://aide.passculture.app',
      isExternal: true,
    },
    cancelText: 'cancel',
    children: 'lorem ipsum dolor sit amet',
  },
}
