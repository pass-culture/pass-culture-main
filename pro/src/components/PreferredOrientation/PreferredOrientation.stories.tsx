import type { StoryObj } from '@storybook/react'

import { PreferredOrientation } from './PreferredOrientation'

export default {
  title: 'components/ImageUploader/PreferredOrientation',
  component: PreferredOrientation,
}

export const Portrait: StoryObj<typeof PreferredOrientation> = {
  args: {
    orientation: 'portrait',
  },
}

export const Landscape: StoryObj<typeof PreferredOrientation> = {
  args: {
    orientation: 'landscape',
  },
}
