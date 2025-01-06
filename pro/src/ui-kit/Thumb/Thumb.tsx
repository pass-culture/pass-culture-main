import cn from 'classnames'

import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Thumb.module.scss'

/**
 * Props for the Thumb component.
 */
interface ThumbProps {
  /**
   * The URL of the thumbnail image.
   */
  url?: string | null
  /**
   * Custom CSS class for additional styling of the thumbnail.
   */
  className?: string
}

/**
 * The Thumb component is used to display a thumbnail image or a default icon if no image URL is provided.
 *
 * ---
 * **Important: Use the `url` prop to provide the image source, or leave it empty to display the default icon.**
 * ---
 *
 * @param {ThumbProps} props - The props for the Thumb component.
 * @returns {JSX.Element} The rendered Thumb component.
 *
 * @example
 * <Thumb url="/path/to/image.jpg" className="custom-class" />
 *
 * @accessibility
 * - **Alt Attribute**: Ensure that the `alt` attribute is properly set to provide context for the image or icon.
 * - **Lazy Loading**: The thumbnail image is loaded lazily to improve performance and reduce initial load time.
 */
export const Thumb = ({ url = '', className }: ThumbProps): JSX.Element => {
  return (
    <div className={styles['thumb-container']}>
      {url ? (
        <img
          className={cn(styles['offer-thumb'], className)}
          loading="lazy"
          src={url}
          alt=""
        />
      ) : (
        <SvgIcon
          alt=""
          src={strokeOfferIcon}
          width="48"
          className={cn(styles['default-thumb'], className)}
        />
      )}
    </div>
  )
}
