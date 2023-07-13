import React from 'react'

import landscapePreferredOrientation from './landscape-preferred-orientation.svg'
import portraitPreferredOrientation from './portrait-preferred-orientation.svg'
import style from './PreferredOrientation.module.scss'

export type PreferredOrientationProps = {
  orientation: 'portrait' | 'landscape'
  children?: never
}

export const PreferredOrientation = ({
  orientation,
}: PreferredOrientationProps): JSX.Element => {
  const imageSrc =
    orientation === 'portrait'
      ? portraitPreferredOrientation
      : landscapePreferredOrientation

  return (
    <figure className={style['preferred-orientation']}>
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
