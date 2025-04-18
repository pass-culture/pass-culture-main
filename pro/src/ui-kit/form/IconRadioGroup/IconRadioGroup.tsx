import { useId } from 'react'

import { IconRadio } from 'ui-kit/formV2/IconRadio/IconRadio'

import { FieldError } from '../shared/FieldError/FieldError'

import styles from './IconRadioGroup.module.scss'

export type IconRadioGroupValues = {
  label: string
  icon: string | JSX.Element
  value: string
}

export interface IconRadioGroupProps {
  name: string
  legend: string
  /**
   * ```
   * {
   *   label: Hidden label for the radio button shown as a tooltip on hover/focus
   *   icon: Icon element displayed in the small round radio button
   *   value: Value of the radio button
   * }
   * ```
   */
  group: IconRadioGroupValues[]
  isOptional?: boolean
  asterisk?: boolean
  error?: string
  required?: boolean
  value: string
  onChange: (value: string) => void
}

export const IconRadioGroup = ({
  group,
  name,
  legend,
  required = false,
  asterisk = true,
  error,
  value,
  onChange,
}: IconRadioGroupProps): JSX.Element => {
  const scaleId = useId()
  const errorId = useId()

  const hasError = Boolean(error)
  const scale =
    group.length > 0 ? [group[0].label, group[group.length - 1].label] : []

  const displayScale = scale.length > 1

  return (
    <>
      <fieldset
        className={styles['icon-radio-group']}
        name={`icon-radio-group-${name}`}
        aria-describedby={`${hasError ? errorId : ''} ${scaleId}`}
      >
        <legend className={styles['icon-radio-group-legend']}>
          {legend}
          {required && asterisk && ' *'}
        </legend>
        {displayScale && (
          <p className={styles['visually-hidden']} id={scaleId}>
            L’échelle de sélection va de {scale[0]} à {scale[1]}
          </p>
        )}
        <div className={styles['icon-radio-group-items-container']}>
          <div className={styles['icon-radio-group-items']}>
            {group.map((item) => (
              <IconRadio
                name={name}
                className={styles['icon-radio-group-item']}
                key={item.label}
                icon={item.icon}
                label={item.label}
                checked={item.value === value}
                hasError={hasError}
                onChange={() => {
                  onChange(item.value)
                }}
              />
            ))}
          </div>
          {displayScale && (
            <div
              className={styles['icon-radio-group-scale']}
              aria-hidden="true"
            >
              {scale.map((s) => (
                <span key={s}>{s}</span>
              ))}
            </div>
          )}
          <div role="alert" id={errorId}>
            {error && (
              <FieldError name={name} className={styles['error']}>
                {error}
              </FieldError>
            )}
          </div>
        </div>
      </fieldset>
    </>
  )
}
