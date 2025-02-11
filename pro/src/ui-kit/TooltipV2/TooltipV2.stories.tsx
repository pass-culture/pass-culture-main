import type { StoryObj } from '@storybook/react'

import { Button } from 'ui-kit/Button/Button'

import { TooltipV2 } from './TooltipV2'

export default {
  title: 'ui-kit/TooltipV2',
  component: TooltipV2,
  decorators: [
    (Story: any) => (
      <div style={{ padding: '4rem' }}>
        <Story />
      </div>
    ),
  ],
}

export const Default: StoryObj<typeof TooltipV2> = {
  args: {
    content: <>Contenu du tooltip</>,
    children: <Button>Je peux afficher un tooltip.</Button>,
  },
}
