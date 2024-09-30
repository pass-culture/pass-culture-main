import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-react-router-v6'

import { Spinner } from './Spinner'

export default {
  title: 'ui-kit/Spinner',
  decorators: [withRouter],
  component: Spinner,
}

export const Default: StoryObj<typeof Spinner> = {
  args: {
    message: 'Chargement en cours',
  },
}
