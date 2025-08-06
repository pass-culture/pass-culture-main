import type { StoryObj } from '@storybook/react'

import { ImageDragAndDrop } from './ImageDragAndDrop'

export default {
  title: '@/components/ImageDragAndDrop/ImageDragAndDrop',
  component: ImageDragAndDrop,
}

export const initialState: StoryObj<typeof ImageDragAndDrop> = {}

export const disabledState: StoryObj<typeof ImageDragAndDrop> = {
  args: {
    disabled: true,
  },
}
