import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { MultiSelect } from './MultiSelect'

export default {
  title: 'ui-kit/MultiSelect',
  decorators: [withRouter],
  component: MultiSelect,
  parameters: {
    docs: {
      story: {
        inline: false,
        iframeHeight: 380,
      },
    },
  },
}

export const Default: StoryObj<typeof MultiSelect> = {
  args: {
    options: [
      { id: '1', label: '78 - Yvelines' },
      { id: '2', label: '75 - Paris' },
      { id: '3', label: '44 - Nantes' },
      { id: '4', label: '76 - Rouen' },
      { id: '5', label: '77 - Seine et Marne' },
    ],
  },
}

export const WithDefaultOptions: StoryObj<typeof MultiSelect> = {
  args: {
    options: [
      { id: '1', label: '78 - Yvelines' },
      { id: '2', label: '75 - Paris' },
      { id: '3', label: '44 - Nantes' },
      { id: '4', label: '76 - Rouen' },
      { id: '5', label: '77 - Seine et Marne' },
    ],
    defaultOptions: [
      { id: '2', label: '75 - Paris' },
      { id: '3', label: '44 - Nantes' },
    ],
  },
}
