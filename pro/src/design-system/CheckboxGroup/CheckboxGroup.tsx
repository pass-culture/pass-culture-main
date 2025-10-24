import classNames from 'classnames'
import fullError from 'icons/full-error.svg'
import { useId } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Checkbox, type CheckboxProps } from '../Checkbox/Checkbox'
import styles from './CheckboxGroup.module.scss'

export type CheckboxGroupOption = Omit<CheckboxProps, 'variant'>

export type CheckboxGroupProps = {
  /** Label for the checkbox group */
  label: React.ReactNode
  description?: string
  /** Error message for the checkbox group */
  error?: string
  /** List of options as checkboxes */
  options: CheckboxGroupOption[]
  /** Controlled selected values */
  /** Display style of the checkbox group, defaults to 'vertical' */
  display?: 'vertical' | 'horizontal'
  /** Variant of the checkboxes (applied to all), defaults to 'default' */
  variant?: 'default' | 'detailed'
  /** If the checkbox group is disabled, making all options unselectable */
  disabled?: boolean
}

export const CheckboxGroup = ({
  label,
  description,
  error,
  options,
  display = 'vertical',
  variant = 'default',
  disabled = false,
}: CheckboxGroupProps) => {
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = `${error ? errorId : ''} ${description ? descriptionId : ''}`

  const isStringLabel = typeof label === 'string'

  return (
    <fieldset
      aria-describedby={describedBy}
      className={classNames(
        styles['checkbox-group'],
        styles[`display-${display}`],
        styles[`variant-${variant}`],
        { [styles['label-as-text']]: isStringLabel }
      )}
    >
      <legend className={styles['checkbox-group-legend']}>{label}</legend>
      {description && (
        <p id={descriptionId} className={styles['checkbox-group-description']}>
          {description}
        </p>
      )}
      <div role="alert">
        {error && (
          <div id={errorId}>
            <SvgIcon
              src={fullError}
              alt=""
              width="16"
              className={styles['checkbox-group-error-icon']}
            />
            <span className={styles['checkbox-group-error']}>{error}</span>
          </div>
        )}
      </div>
      <div className={styles['checkbox-group-options']}>
        {options.map((option) => {
          return (
            <div className={styles['checkbox-group-item']} key={option.label}>
              {variant === 'default' ? (
                <Checkbox
                  {...option}
                  description={undefined}
                  asset={undefined}
                  collapsed={undefined}
                  hasError={!!error}
                  disabled={disabled || option.disabled}
                  variant="default"
                />
              ) : (
                <Checkbox
                  {...option}
                  hasError={!!error}
                  disabled={disabled || option.disabled}
                  variant="detailed"
                />
              )}
            </div>
          )
        })}
      </div>
    </fieldset>
  )
}
