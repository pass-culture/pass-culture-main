import cn from 'classnames'
import React from 'react'

import { UploaderModeEnum } from '../types'

import style from './ImagePreview.module.scss'

export type IImagePreviewProps = {
  imageUrl: string
  children?: never
  alt: string
  mode: UploaderModeEnum
}

const ImagePreview = ({ imageUrl, alt, mode }: IImagePreviewProps) => (
  <img
    alt={alt}
    className={cn(style['image-preview'], {
      [style['preview-venue']]: mode === UploaderModeEnum.VENUE,
      [style['preview-offer']]: mode === UploaderModeEnum.OFFER,
    })}
    src={imageUrl}
  />
)

export default ImagePreview
