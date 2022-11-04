import type { Story } from '@storybook/react'
import React from 'react'

import StoreProvider from 'store/StoreProvider/StoreProvider'

import ImageUploader, { IImageUploaderProps } from './ImageUploader'
import sampleImageLandscape from './sample-image-landscape.jpg'
import sampleImagePortrait from './sample-image-portrait.jpg'
import { UploaderModeEnum } from './types'

export default {
  title: 'components/ImageUploader',
  component: ImageUploader,
}

const Template: Story<IImageUploaderProps> = props => (
  <StoreProvider isDev>
    <ImageUploader {...props} />
  </StoreProvider>
)

const props: IImageUploaderProps = {
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
  onImageDelete: async () => {
    alert('onDelete have been called.')
  },
  onImageUpload: async () => {
    alert('onImageUpload have been called.')
  },
}

export const WithImageOffer = Template.bind({})
WithImageOffer.args = {
  ...props,
}

export const WithImageVenue = Template.bind({})
WithImageVenue.args = {
  ...props,
  initialValues: {
    imageUrl: sampleImageLandscape,
    originalImageUrl: sampleImageLandscape,
  },
  mode: UploaderModeEnum.VENUE,
}

export const WithoutImage = Template.bind({})
WithoutImage.args = {
  mode: UploaderModeEnum.OFFER,
}
