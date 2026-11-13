import cn from 'classnames'

import strokeNoImageIcon from '@/icons/stroke-no-image.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ImagePlaceholder.module.scss'

type ImagePlaceholderProps = {
  className?: string
  isVideo?: boolean
  alt?: string
}

export function ImagePlaceholder({
  className,
  isVideo,
  alt,
}: Readonly<ImagePlaceholderProps>) {
  const message = isVideo
    ? 'Aperçu vidéo corrompu, veuillez ajouter une nouvelle vidéo'
    : 'Image corrompue, veuillez ajouter une nouvelle image'

  return (
    <div
      className={cn(styles['image-placeholder'], className)}
      role="img"
      aria-label={alt ? `${alt}. ${message}` : message}
    >
      <SvgIcon alt="" src={strokeNoImageIcon} width="48" />
      <p className={styles['image-placeholder-text']}>{message}</p>
    </div>
  )
}
