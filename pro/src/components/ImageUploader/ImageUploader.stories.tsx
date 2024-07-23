import type { StoryObj } from '@storybook/react'

import { ImageUploader, ImageUploaderProps } from './ImageUploader'
import sampleImageLandscape from './sample-image-landscape.jpg'
import sampleImagePortrait from './sample-image-portrait.jpg'
import { UploaderModeEnum } from './types'

export default {
  title: 'components/ImageUploader/ImageUploader',
  component: ImageUploader,
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
