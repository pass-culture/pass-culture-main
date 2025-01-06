import type { StoryObj } from '@storybook/react'

import { InfoBox } from './InfoBox'

export default {
  title: 'ui-kit/InfoBox',
  component: InfoBox,
  decorators: [
    (Story: any) => (
      <div style={{ maxWidth: '316px' }}>
        <Story />
      </div>
    ),
  ],
}

export const InfoWithLink: StoryObj<typeof InfoBox> = {
  args: {
    link: { text: 'Suivre le lien', to: '#', isExternal: true },
    children:
      'Molestie fermentum accumsan at faucibus leo massa proin. Suspendisse sed sed fringilla ipsum adipiscing.',
  },
}

export const InfoWithoutLink: StoryObj<typeof InfoBox> = {
  args: {
    children:
      'Molestie fermentum accumsan at faucibus leo massa proin. Suspendisse sed sed fringilla ipsum adipiscing.',
  },
}
