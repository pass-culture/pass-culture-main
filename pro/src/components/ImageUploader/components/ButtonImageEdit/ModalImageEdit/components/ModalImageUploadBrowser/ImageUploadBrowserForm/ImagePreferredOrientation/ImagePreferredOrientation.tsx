import React from 'react'

import style from './ImagePreferredOrientation.module.scss'
import landscapePreferredOrientation from './landscape-preferred-orientation.svg'
import portraitPreferredOrientation from './portrait-preferred-orientation.svg'

type ImagePreferredOrientationProps = {
  orientation: 'portrait' | 'landscape'
  children?: never
  id: string
}

export const ImagePreferredOrientation = ({
  orientation,
  id,
}: ImagePreferredOrientationProps): JSX.Element => {
  const imageSrc =
    orientation === 'portrait'
      ? portraitPreferredOrientation
      : landscapePreferredOrientation

  return (
    <figure id={id} className={style['preferred-orientation']}>
      <div className={style['preferred-orientation-image-container']}>
        <img src={imageSrc} alt="" />
      </div>
      <figcaption className={style['preferred-orientation-label']}>
        {orientation === 'portrait'
          ? 'Utilisez de préférence un visuel en orientation portrait'
          : 'Utilisez de préférence un visuel en orientation paysage'}
      </figcaption>
    </figure>
  )
}
