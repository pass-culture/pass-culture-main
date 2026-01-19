import type { StoryObj } from '@storybook/react-vite'


import { Tooltip } from './Tooltip'
import { Button } from '@/design-system/Button/Button';

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
    children: <Button label="Je peux afficher un tooltip."/>,
  },
}
