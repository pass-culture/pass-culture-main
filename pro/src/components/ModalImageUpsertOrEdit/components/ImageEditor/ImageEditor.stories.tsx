/* istanbul ignore file: not needed */
import type { StoryObj } from '@storybook/react'

import { ImageEditor } from './ImageEditor'
import sampleImage from './sample-image.jpg'

export default {
  title: 'components/ImageUploader/ImageEditorInModalUpsertOrEdit',
  component: ImageEditor,
  decorators: [(Story: any) => <Story />],
}

export const Default: StoryObj<typeof ImageEditor> = {
  args: {
    canvasHeight: 300,
    canvasWidth: 400,
    cropBorderColor: '#FFF',
    cropBorderHeight: 30,
    cropBorderWidth: 40,
    image: sampleImage as unknown as File,
  },
}
