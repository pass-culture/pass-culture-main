import cn from 'classnames'
import React from 'react'

import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Thumb.module.scss'

interface ThumbProps {
  url?: string | null
  className?: string
}

export const Thumb = ({ url = '', className }: ThumbProps) => {
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
