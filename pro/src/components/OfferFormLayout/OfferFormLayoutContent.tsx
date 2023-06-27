import cn from 'classnames'
import React from 'react'

import style from './OfferFormLayout.module.scss'

interface OfferFormLayoutContentProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutContent = ({
  children,
  className,
}: OfferFormLayoutContentProps): JSX.Element => (
  <div className={cn(style['content'], className)}>{children}</div>
)

export default OfferFormLayoutContent
