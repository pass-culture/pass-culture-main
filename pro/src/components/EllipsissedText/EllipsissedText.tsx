import classnames from 'classnames'
import type { HTMLProps } from 'react'

import styles from './EllipsissedText.module.scss'

export const EllipsissedText = ({
  className,
  ...rest
}: Readonly<HTMLProps<HTMLSpanElement>>) => (
  <span
    className={classnames(styles['ellipsissed-text'], className)}
    {...rest}
  />
)
