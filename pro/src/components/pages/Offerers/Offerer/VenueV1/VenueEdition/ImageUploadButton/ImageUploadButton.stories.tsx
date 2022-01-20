import { Story } from '@storybook/react'
import React from 'react'

import { ImageUploadButton, ImageUploadButtonProps } from './ImageUploadButton'

export default {
  title: 'components/ImageUploadButton',
  component: ImageUploadButton,
}

export const Add: Story<ImageUploadButtonProps> = props => (
  <ImageUploadButton {...props} />
)
