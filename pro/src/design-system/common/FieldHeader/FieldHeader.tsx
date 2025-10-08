import classNames from 'classnames'

import styles from './FieldHeader.module.scss'

type FieldHeaderProps = {
  fieldId: string
  label: string
  required: boolean
  asterisk?: boolean
  description?: string
  descriptionId?: string
}

export function FieldHeader({
  fieldId,
  label,
  required,
  asterisk,
  description,
  descriptionId,
}: FieldHeaderProps) {
  return (
    <div
      className={classNames({
        [styles['has-description']]: Boolean(description),
      })}
    >
      <label htmlFor={fieldId} className={styles['label']}>
        {label}
        {required && asterisk && (
          <span className={styles['label-mandatory-asterisk']}>*</span>
        )}
      </label>
      {description && (
        <p id={descriptionId} className={styles['description']}>
          {description}
        </p>
      )}
    </div>
  )
}
