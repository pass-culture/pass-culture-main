import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Spinner } from './Spinner'

export default {
  title: '@/ui-kit/Spinner',
  decorators: [withRouter],
  component: Spinner,
}

export const Default: StoryObj<typeof Spinner> = {
  args: {
    message: 'Chargement en cours',
  },
}
