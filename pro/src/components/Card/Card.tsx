import cn from 'classnames'
import React from 'react'

import styles from './Card.module.scss'

interface CardProps extends React.HTMLProps<HTMLDivElement> {
  children: React.ReactNode
}

export const Card = ({ children, className, ...rest }: CardProps) => (
  <div className={cn(styles['container'], className)} {...rest}>
    {children}
  </div>
)
