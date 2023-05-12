import classnames from 'classnames'
import React, { FC } from 'react'

import styles from './Divider.module.scss'

type Size = 'medium' | 'large'

export interface DividerProps {
  size?: Size
  className?: string
}

const Divider: FC<DividerProps> = ({ size, className }) => {
  const sizeClassName = {
    medium: styles['divider-medium'],
    large: styles['divider-large'],
  }[size || 'medium']

  return (
    <div className={classnames(styles.divider, sizeClassName, className)} />
  )
}
export default Divider
