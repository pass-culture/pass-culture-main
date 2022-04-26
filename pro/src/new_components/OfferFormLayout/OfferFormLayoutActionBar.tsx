import cn from 'classnames'
import React from 'react'

import style from './OfferFormLayout.module.scss'

interface IOfferFormLayoutActionBarProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutActionBar = ({
  children,
  className,
}: IOfferFormLayoutActionBarProps): JSX.Element => (
  <div className={cn(style['action-bar'], className)}>
    <div className={cn(style['inner'], className)}>{children}</div>
  </div>
)

export default OfferFormLayoutActionBar
