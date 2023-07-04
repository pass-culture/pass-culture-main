import cn from 'classnames'
import React from 'react'

import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Thumb.module.scss'

interface ThumbProps {
  url?: string | null
  alt?: string
  className?: string
}

const Thumb = ({ url = '', alt = '', className }: ThumbProps) => {
  return url ? (
    <img
      alt={alt}
      className={cn(styles['offer-thumb'], className)}
      loading="lazy"
      src={url}
    />
  ) : (
    <div className={cn(styles['default-thumb'], className)}>
      <SvgIcon alt={alt} src={strokeOfferIcon} />
    </div>
  )
}

export default Thumb
