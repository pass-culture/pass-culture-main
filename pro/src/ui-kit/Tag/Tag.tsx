import cx from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tag.module.scss'

interface TagProps {
  className?: string
  children: ReactNode
}

export const Tag = ({ children, className }: TagProps): JSX.Element => {
  return <span className={cx(styles['tag'], className)}>{children}</span>
}
