import React from 'react'
import cx from 'classnames'
import styles from './Tag.module.scss'

interface ITagProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const Tag = ({ children, className }: ITagProps): JSX.Element => (
  <span className={cx(styles.tag, className)}>{children}</span>
)

export default Tag
