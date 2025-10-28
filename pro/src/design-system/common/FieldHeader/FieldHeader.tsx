import classNames from 'classnames'

import type { RequiredIndicator } from '../types'
import styles from './FieldHeader.module.scss'

type FieldHeaderProps = {
  fieldId: string
  label: string
  required: boolean
  requiredIndicator?: RequiredIndicator
  description?: string
  descriptionId?: string
}

export function FieldHeader({
  fieldId,
  label,
  required,
  requiredIndicator,
  description,
  descriptionId,
}: FieldHeaderProps) {
  return (
    <div
      className={classNames(styles['field-header'], {
        [styles['has-description']]: Boolean(description),
      })}
    >
      <div className={styles['field-header-left']}>
        <label htmlFor={fieldId} className={styles['label']}>
          {label}
          {required && requiredIndicator === 'symbol' && (
            <span className={styles['label-mandatory-symbol']}>*</span>
          )}
        </label>
        {description && (
          <p id={descriptionId} className={styles['description']}>
            {description}
          </p>
        )}
      </div>
      {required && requiredIndicator === 'explicit' && (
        <div className={styles['field-header-right']}>Obligatoire</div>
      )}
    </div>
  )
}
