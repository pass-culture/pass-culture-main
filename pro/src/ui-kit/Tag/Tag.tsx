import cx from 'classnames'
import React, { ReactNode } from 'react'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Tag.module.scss'

interface Closeable {
  onClose?: (event: React.MouseEvent<HTMLButtonElement>) => void
  closeLabel?: string
  disabled?: boolean
}
interface TagProps {
  className?: string
  closeable?: Closeable
  children: ReactNode
}

const Tag = ({ children, className, closeable }: TagProps): JSX.Element => {
  return (
    <span
      className={cx(
        styles.tag,
        closeable ? styles['tag-closeable'] : null,
        className
      )}
    >
      {closeable ? (
        <button
          className={cx(styles['tag-close-button'], {
            [styles['tag-close-button--disabled']]: closeable.disabled,
          })}
          onClick={closeable.onClose}
          title={closeable.closeLabel}
          type="button"
          disabled={closeable.disabled}
        >
          {children}
          <SvgIcon
            src={strokeCloseIcon}
            alt={closeable.closeLabel ?? ''}
            className={styles['tag-close-button-icon']}
          />
        </button>
      ) : (
        <>{children}</>
      )}
    </span>
  )
}

export default Tag
