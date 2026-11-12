import classNames from 'classnames'

import type { RequiredIndicator } from '../types'
import styles from './FieldHeader.module.scss'

type FieldHeaderProps = {
  fieldId: string
  label?: string | JSX.Element
  /** Id of the label, to reference it from `aria-labelledby` */
  labelId?: string
  required: boolean
  requiredIndicator?: RequiredIndicator
  description?: string
  descriptionId?: string
  labelVariant?: 'body' | 'title3'
}

export function FieldHeader({
  fieldId,
  label,
  labelId,
  required,
  requiredIndicator,
  description,
  descriptionId,
  labelVariant = 'body',
}: Readonly<FieldHeaderProps>) {
  return (
    <div
      className={classNames(styles['field-header'], {
        [styles['has-description']]: Boolean(description),
        [styles['label-variant-title3']]: labelVariant === 'title3',
      })}
    >
      <div>
        {label && (
          <label id={labelId} htmlFor={fieldId} className={styles['label']}>
            <span>{label}</span>
            {required && requiredIndicator === 'symbol' && (
              <span className={styles['label-mandatory-symbol']}>*</span>
            )}
          </label>
        )}
        {description && (
          <p id={descriptionId} className={styles['description']}>
            {description}
          </p>
        )}
      </div>
      {required && requiredIndicator === 'explicit' && (
        <p className={styles['field-header-right']}>Obligatoire</p>
      )}
    </div>
  )
}
