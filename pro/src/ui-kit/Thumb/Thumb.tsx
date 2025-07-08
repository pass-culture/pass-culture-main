import cn from 'classnames'

import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Thumb.module.scss'

/**
 * Props for the Thumb component.
 */
interface ThumbProps {
  /**
   * The URL of the thumbnail image. If it is not provided, a fallback icon is displayed.
   */
  url?: string | null
  className?: string
  /**
   * The accessible label of the image or fallback icon.
   */
  alt?: string
}

/**
 * The Thumb component is used to display a thumbnail image or a default icon if no image URL is provided.
 */
export const Thumb = ({
  url = '',
  className,
  alt = '',
}: ThumbProps): JSX.Element => {
  return (
    <div className={styles['thumb-container']}>
      {url ? (
        <img
          className={cn(styles['offer-thumb'], className)}
          loading="lazy"
          src={url}
          alt={alt}
        />
      ) : (
        <SvgIcon
          alt={alt}
          src={strokeOfferIcon}
          width="48"
          data-testid="thumb-icon"
          className={cn(styles['default-thumb'], className)}
        />
      )}
    </div>
  )
}
