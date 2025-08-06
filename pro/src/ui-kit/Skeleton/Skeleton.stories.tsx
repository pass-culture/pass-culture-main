import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Skeleton } from './Skeleton'

export default {
  title: '@/ui-kit/Skeleton',
  decorators: [withRouter],
  component: Skeleton,
}

export const Default: StoryObj<typeof Skeleton> = {
  args: {
    height: '2.5rem',
    width: '80%',
  },
}

export const Rounded: StoryObj<typeof Skeleton> = {
  args: {
    height: '2.5rem',
    width: '2.5rem',
    roundedFull: true,
  },
}
