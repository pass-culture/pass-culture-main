import cn from 'classnames'
import type React from 'react'

import styles from './CardBis.module.scss'

interface CardProps extends React.HTMLProps<HTMLDivElement> {
  children: React.ReactNode
}

export const CardBis = ({ children, className, ...rest }: CardProps) => (
  <div className={cn(styles['container'], className)} {...rest}>
    {children}
  </div>
)
