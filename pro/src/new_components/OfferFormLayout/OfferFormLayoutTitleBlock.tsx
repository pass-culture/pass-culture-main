import cn from 'classnames'
import React from 'react'

import style from './OfferFormLayout.module.scss'

interface IOfferFormLayoutTitleBlockProps {
  actions?: React.ReactNode
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const OfferFormLayoutTitleBlock = ({
  actions,
  children,
  className,
}: IOfferFormLayoutTitleBlockProps): JSX.Element => (
  <div className={cn(style['title'], className)}>
    <div>{children}</div>
    {actions && <div className={style['right']}>{actions}</div>}
  </div>
)

export default OfferFormLayoutTitleBlock
