import cn from 'classnames'
import React from 'react'

import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Thumb.module.scss'

interface ThumbProps {
  url?: string | null
  className?: string
}

const Thumb = ({ url = '', className }: ThumbProps) => {
  return url ? (
    <img
      className={cn(styles['offer-thumb'], className)}
      loading="lazy"
      src={url}
    />
  ) : (
    <SvgIcon
      alt=""
      src={strokeOfferIcon}
      width="40"
      className={cn(styles['default-thumb'], className)}
    />
  )
}

export default Thumb
