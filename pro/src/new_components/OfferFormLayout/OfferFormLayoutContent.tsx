import React from 'react'
import cn from 'classnames'
import style from './OfferFormLayout.module.scss'

interface IOfferFormLayoutContentProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutContent = ({
  children,
  className,
}: IOfferFormLayoutContentProps): JSX.Element => (
  <div className={cn(style['content'], className)}>{children}</div>
)

export default OfferFormLayoutContent
