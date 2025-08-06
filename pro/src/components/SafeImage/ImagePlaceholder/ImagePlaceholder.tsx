import cn from 'classnames'

import strokeNoImageIcon from '@/icons/stroke-no-image.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ImagePlaceholder.module.scss'

type ImagePlaceholderProps = {
  className?: string
}

export function ImagePlaceholder({ className }: ImagePlaceholderProps) {
  return (
    <div className={cn(styles['image-placeholder'], className)}>
      <SvgIcon alt="" src={strokeNoImageIcon} width="48" />
      <p className={styles['image-placeholder-text']}>
        Image corrompue, veuillez ajouter une nouvelle image
      </p>
    </div>
  )
}
