import type { StoryObj } from '@storybook/react'
import { Provider } from 'react-redux'
import { withRouter } from 'storybook-addon-remix-react-router'

import { configureTestStore } from 'commons/store/testUtils'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'

import sampleImageLandscape from './assets/sample-image-landscape.jpg'
import sampleImagePortrait from './assets/sample-image-portrait.jpg'
import { ImageUploader, ImageUploaderProps } from './ImageUploader'

export default {
  title: 'components/ImageUploader/ImageUploader',
  component: ImageUploader,
  decorators: [
    withRouter,
    (Story: any) => (
      <Provider store={configureTestStore({})}>
        <Story />
      </Provider>
    ),
  ],
}

const props: ImageUploaderProps = {
  initialValues: {
    originalImageUrl: sampleImagePortrait,
    imageUrl: sampleImagePortrait,
    credit: 'John Do',
    cropParams: {
      xCropPercent: 0,
      yCropPercent: 0,
      heightCropPercent: 1,
      widthCropPercent: 1,
    },
  },
  mode: UploaderModeEnum.OFFER,
  onImageDelete: () => {
    alert('onDelete have been called.')
  },
  onImageUpload: () => {
    alert('onImageUpload have been called.')
  },
}

export const WithImageOffer: StoryObj<typeof ImageUploader> = {
  args: {
    ...props,
  },
}

export const WithImageVenue: StoryObj<typeof ImageUploader> = {
  args: {
    ...props,
    initialValues: {
      imageUrl: sampleImageLandscape,
      originalImageUrl: sampleImageLandscape,
    },
    mode: UploaderModeEnum.VENUE,
  },
}

export const WithoutImage: StoryObj<typeof ImageUploader> = {
  args: {
    mode: UploaderModeEnum.OFFER,
  },
}
