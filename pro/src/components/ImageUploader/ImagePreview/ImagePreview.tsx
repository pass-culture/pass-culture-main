import cn from 'classnames'
import React from 'react'

import { UploaderModeEnum } from '../types'

import style from './ImagePreview.module.scss'

type ImagePreviewProps = {
  imageUrl: string
  children?: never
  alt: string
  mode: UploaderModeEnum
}

const ImagePreview = ({ imageUrl, alt, mode }: ImagePreviewProps) => (
  <img
    alt={alt}
    className={cn(style['image-preview'], {
      [style['preview-venue']]: mode === UploaderModeEnum.VENUE,
      [style['preview-offer']]:
        mode === UploaderModeEnum.OFFER ||
        mode === UploaderModeEnum.OFFER_COLLECTIVE,
    })}
    src={imageUrl}
  />
)

export default ImagePreview
