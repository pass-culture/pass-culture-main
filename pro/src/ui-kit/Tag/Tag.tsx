import cx from 'classnames'
import React from 'react'

import styles from './Tag.module.scss'

interface ITagProps {
  children: JSX.Element
  className?: string
}

const Tag = ({ children, className }: ITagProps): JSX.Element => (
  <span className={cx(styles.tag, className)}>{children}</span>
)

export default Tag
