import React from 'react'

import style from './ImagePreview.module.scss'

export type IImagePreviewProps = {
  imageUrl: string
  children?: never
  alt: string
}

const ImagePreview = ({ imageUrl, alt }: IImagePreviewProps) => (
  <img alt={alt} className={style['image-preview']} src={imageUrl} />
)

export default ImagePreview
