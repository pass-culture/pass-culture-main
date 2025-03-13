import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Skeleton } from './Skeleton'

export default {
  title: 'ui-kit/Skeleton',
  decorators: [withRouter],
  component: Skeleton,
}

export const Default: StoryObj<typeof Skeleton> = {
  args: {
    height: '40px',
    width: '80%',
  },
}

export const Rounded: StoryObj<typeof Skeleton> = {
  args: {
    height: '40px',
    width: '40px',
    roundedFull: true,
  },
}
