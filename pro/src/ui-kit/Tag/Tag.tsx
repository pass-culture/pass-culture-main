import cx from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tag.module.scss'

export enum TagVariant {
  SMALL_OUTLINE = 'small-outline',
  GREY = 'grey',
}

const classByVariant: Record<TagVariant, string> = {
  [TagVariant.SMALL_OUTLINE]: styles['small-outline'],
  [TagVariant.GREY]: styles['grey'],
}

interface TagProps {
  className?: string
  children: ReactNode
  variant: TagVariant
}

export const Tag = ({
  children,
  className,
  variant,
}: TagProps): JSX.Element => (
  <span className={cx(styles['tag'], classByVariant[variant], className)}>
    {children}
  </span>
)
