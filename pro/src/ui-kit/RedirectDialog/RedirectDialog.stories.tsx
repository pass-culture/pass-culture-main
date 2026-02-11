import type { StoryObj } from '@storybook/react-vite'

import { RedirectDialog } from './RedirectDialog'

export default {
  title: '@/components/Dialog/RedirectDialog',
  component: RedirectDialog,
}

export const Default: StoryObj<typeof RedirectDialog> = {
  args: {
    open: true,
    title: 'title',
    redirectText: 'Go to ...',
    to: 'https://aide.passculture.app',
    isExternal: true,
    cancelText: 'cancel',
    children: 'lorem ipsum dolor sit amet',
  },
}
