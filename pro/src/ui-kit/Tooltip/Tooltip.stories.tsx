import type { StoryObj } from '@storybook/react'

import { Tooltip } from './Tooltip'

export default {
  title: 'ui-kit/Tooltip',
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
    children: 'Hover me!',
  },
}
