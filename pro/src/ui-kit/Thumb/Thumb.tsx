import cn from 'classnames'
import React from 'react'

import { ReactComponent as SVGOffers } from 'icons/ico-placeholder-offer-image.svg'

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
      <SVGOffers title={alt} />
    </div>
  )
}

export default Thumb
