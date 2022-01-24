import React, { FunctionComponent } from 'react'

import { ReactComponent as LandscapePreferredOrientation } from './landscape-preferred-orientation.svg'
import { ReactComponent as PortraitPreferredOrientation } from './portrait-preferred-orientation.svg'
import style from './PreferredOrientation.module.scss'

export type PreferredOrientationProps = {
  orientation: 'portrait' | 'landscape'
  children?: never
}

export const PreferredOrientation: FunctionComponent<PreferredOrientationProps> =
  ({ orientation }) => {
    const Image =
      orientation === 'portrait'
        ? PortraitPreferredOrientation
        : LandscapePreferredOrientation

    return (
      <figure className={style['preferred-orientation']}>
        <div className={style['preferred-orientation-image-container']}>
          <Image />
        </div>
        <figcaption className={style['preferred-orientation-label']}>
          {orientation === 'portrait'
            ? 'Utilisez de préférence un visuel en orientation portrait'
            : 'Utilisez de préférence un visuel en orientation paysage'}
        </figcaption>
      </figure>
    )
  }
