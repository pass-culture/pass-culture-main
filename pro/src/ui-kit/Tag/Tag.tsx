import cx from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tag.module.scss'

export enum TagVariant {
  SMALL_OUTLINE = 'small-outline',
  LIGHT_GREY = 'light-grey',
  LIGHT_PURPLE = 'light-purple',
}

const classByVariant: Record<TagVariant, string> = {
  [TagVariant.SMALL_OUTLINE]: styles['small-outline'],
  [TagVariant.LIGHT_GREY]: styles['light-grey'],
  [TagVariant.LIGHT_PURPLE]: styles['light-purple'],
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
