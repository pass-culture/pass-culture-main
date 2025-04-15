import style from './ImagePreferredOrientation.module.scss'
import { LandscapePreferredOrientationSVG } from './LandscapePreferredOrientationSVG'
import { PortraitPreferredOrientationSVG } from './PortraitPreferredOrientationSVG'

type ImagePreferredOrientationProps = {
  orientation: 'portrait' | 'landscape'
  children?: never
  id: string
}

export const ImagePreferredOrientation = ({
  orientation,
  id,
}: ImagePreferredOrientationProps): JSX.Element => {
  return (
    <figure id={id} className={style['preferred-orientation']}>
      <div className={style['preferred-orientation-image-container']}>
        {orientation === 'portrait' ? (
          <PortraitPreferredOrientationSVG />
        ) : (
          <LandscapePreferredOrientationSVG />
        )}
      </div>
      <figcaption className={style['preferred-orientation-label']}>
        {orientation === 'portrait'
          ? 'Utilisez de préférence un visuel en orientation portrait'
          : 'Utilisez de préférence un visuel en orientation paysage'}
      </figcaption>
    </figure>
  )
}
