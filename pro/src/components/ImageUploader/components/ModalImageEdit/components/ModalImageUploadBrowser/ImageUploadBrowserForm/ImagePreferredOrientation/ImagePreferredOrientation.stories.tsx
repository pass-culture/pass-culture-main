import type { StoryObj } from '@storybook/react'

import { ImagePreferredOrientation } from './ImagePreferredOrientation'

export default {
  title: 'components/ImageUploader/ImagePreferredOrientation',
  component: ImagePreferredOrientation,
}

export const Portrait: StoryObj<typeof ImagePreferredOrientation> = {
  args: {
    orientation: 'portrait',
  },
}

export const Landscape: StoryObj<typeof ImagePreferredOrientation> = {
  args: {
    orientation: 'landscape',
  },
}
