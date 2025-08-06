import type { StoryObj } from '@storybook/react'

import { Button } from '@/ui-kit/Button/Button'

import { Tooltip } from './Tooltip'

export default {
  title: '@/ui-kit/Tooltip',
  component: Tooltip,
  decorators: [
    (Story: any) => (
      <div style={{ padding: '4rem' }}>
        <Story />
      </div>
    ),
  ],
}

export const Default: StoryObj<typeof Tooltip> = {
  args: {
    content: 'Contenu du tooltip',
    children: <Button>Je peux afficher un tooltip.</Button>,
  },
}
