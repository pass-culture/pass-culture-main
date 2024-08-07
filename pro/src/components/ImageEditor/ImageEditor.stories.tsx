/* istanbul ignore file: not needed */
import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { ImageEditor } from './ImageEditor'
import sampleImage from './sample-image.jpg'

export default {
  title: 'components/ImageUploader/ImageEditor',
  component: ImageEditor,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ scale: 0 }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
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
