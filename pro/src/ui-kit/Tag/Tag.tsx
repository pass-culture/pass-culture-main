import Icon from 'components/layout/Icon'
import React from 'react'
import cx from 'classnames'
import styles from './Tag.module.scss'
interface Closeable {
  onClose?: (event: React.MouseEvent<HTMLButtonElement>) => void
  closeLabel?: string
}
interface ITagProps {
  className?: string
  closeable?: Closeable
  label: string
}

const Tag = ({ label, className, closeable }: ITagProps): JSX.Element => {
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
          className={styles['tag-close-button']}
          onClick={closeable.onClose}
          title={closeable.closeLabel}
          type="button"
        >
          {label}
          <Icon
            alt={closeable.closeLabel}
            className={styles['tag-close-button-icon']}
            svg="close-tag"
          />
        </button>
      ) : (
        <>{label}</>
      )}
    </span>
  )
}

export default Tag
