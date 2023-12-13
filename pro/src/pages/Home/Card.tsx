import cn from 'classnames'
import React from 'react'

import styles from './Card.module.scss'

interface CardProps extends React.HTMLProps<HTMLDivElement> {
  children: React.ReactNode
  noPaddingBottom?: boolean
}

export const Card = ({
  children,
  noPaddingBottom,
  className,
  ...rest
}: CardProps) => (
  <div
    className={cn(styles['container'], className, {
      [styles['no-padding-bottom']]: noPaddingBottom,
    })}
    {...rest}
  >
    <div className={styles['inner']}>{children}</div>
  </div>
)
