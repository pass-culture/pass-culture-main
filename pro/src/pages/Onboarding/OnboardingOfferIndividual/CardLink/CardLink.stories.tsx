import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { CardLink } from './CardLink'

export default {
  title: 'ui-kit/CardLink',
  decorators: [withRouter],
  component: CardLink,
}

export const Default: StoryObj<typeof CardLink> = {
  args: {
    /* … */
  },
}
