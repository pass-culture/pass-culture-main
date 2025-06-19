import cn from 'classnames'

import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import strokeNoImageIcon from 'icons/stroke-no-image.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ImagePlaceholder.module.scss'

type ImagePlaceholderProps = {
  mode: UploaderModeEnum
}

export function ImagePlaceholder({ mode }: ImagePlaceholderProps) {
  return (
    <div
      className={cn(styles['image-placeholder'], {
        [styles['placeholder-venue']]: mode === UploaderModeEnum.VENUE,
        [styles['placeholder-offer']]:
          mode === UploaderModeEnum.OFFER ||
          mode === UploaderModeEnum.OFFER_COLLECTIVE,
      })}
    >
      <SvgIcon alt="" src={strokeNoImageIcon} width="48" />
      <p className={styles['image-placeholder-text']}>
        Image corrompue, veuillez ajouter une nouvelle image
      </p>
    </div>
  )
}
