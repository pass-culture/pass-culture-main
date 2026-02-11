import type { StoryObj } from '@storybook/react-vite'

import { CardBis } from './CardBis'

export default {
  title: '@/ui-kit/CardBis',
  component: CardBis,
}

export const Default: StoryObj<typeof CardBis> = {
  args: {
    children: 'Hello world',
  },
}

