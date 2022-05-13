import { ImageUploadButton, ImageUploadButtonProps } from './ImageUploadButton'

import React from 'react'
import { Story } from '@storybook/react'

export default {
  title: 'components/ImageUploadButton',
  component: ImageUploadButton,
}

export const Add: Story<ImageUploadButtonProps> = props => (
  <ImageUploadButton {...props} />
)
