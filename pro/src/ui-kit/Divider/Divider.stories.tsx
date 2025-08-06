import type { StoryObj } from '@storybook/react'

import { Divider } from './Divider'

export default {
  title: '@/ui-kit/Divider',
  component: Divider,
  decorators: [
    (Story: any) => (
      <div>
        <p>First text</p>
        <Story />
        <p>Second text</p>
      </div>
    ),
  ],
}

export const Default: StoryObj<typeof Divider> = {
  args: {
    size: 'medium',
  },
}
