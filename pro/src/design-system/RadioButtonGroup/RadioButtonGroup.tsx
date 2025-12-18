import { default as classNames, default as cn } from 'classnames'
import { useId } from 'react'

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import {
  RadioButton,
  type RadioButtonProps,
} from '@/design-system/RadioButton/RadioButton'
import fullErrorIcon from '@/icons/full-error.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButtonGroup.module.scss'

export type RadioButtonGroupProps = {
  /** Name of the radio button group, binding all radio buttons together */
  name: string
  /** Label for the radio button group */
  label: React.ReactNode
  /** List of options as radio buttons */
  options: Array<Omit<RadioButtonProps, 'name'>>
  description?: string
  /** Error message for the radio button group */
  error?: string
  /** Variant of the radio buttons (applied to all), defaults to 'default' */
  variant?: RadioButtonProps['variant']
  /** Sizing of the radio buttons (applied to all), defaults to 'fill' */
  sizing?: RadioButtonProps['sizing']
  /** Asset of the radio buttons (applied to all), displayed when variant is 'detailed' */
  asset?: RadioButtonProps['asset']
  /** Display style of the radio button group, defaults to 'vertical' */
  display?: 'horizontal' | 'vertical'
  /** Selected option, required if the group is non-controlled */
  checkedOption?: string
  /** If the radio button group is disabled, making all options unselectable */
  disabled?: boolean
  /** Event handler for change */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  /** Event handler for blur */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

export const RadioButtonGroup = ({
  name,
  label,
  options,
  description,
  error,
  variant = 'default',
  sizing = 'fill',
  display = 'vertical',
  disabled = false,
  checkedOption,
  asset,
  onChange,
  onBlur,
}: RadioButtonGroupProps): JSX.Element => {
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = `${error ? errorId : ''}${description ? ` ${descriptionId}` : ''}`

  const isStringLabel = typeof label === 'string'

  // Ensure all options have distinct values, which is natural
  // for radio buttons but also a requirement since they are used as unique keys.
  const values = options.map((option) => option.value)
  assertOrFrontendError(
    new Set(values).size === values.length,
    'RadioButtonGroup options must have unique values.'
  )

  return (
    <fieldset
      aria-describedby={describedBy}
      className={classNames(styles['radio-button-group'], {
        [styles['label-as-text']]: isStringLabel,
      })}
    >
      <legend className={styles['radio-button-group-legend']}>{label}</legend>
      <div className={styles['radio-button-group-header']}>
        {description && (
          <span
            id={descriptionId}
            className={styles['radio-button-group-description']}
            // Description might change based on selection,
            // so an aria-live is needed to announce changes.
            aria-live="polite"
          >
            {description}
          </span>
        )}
        <div role="alert" id={errorId}>
          {error && (
            <span className={styles['radio-button-group-error']}>
              <SvgIcon
                className={styles['radio-button-group-error-icon']}
                src={fullErrorIcon}
                alt="Erreur"
              />
              {error}
            </span>
          )}
        </div>
      </div>
      <div
        className={cn(
          styles['radio-button-group-options'],
          styles[`display-${display}`],
          styles[`sizing-${sizing}`],
          styles[`variant-${variant}`]
        )}
      >
        {options.map((optionProps) => (
          <div
            className={styles['radio-button-group-option']}
            key={optionProps.value}
          >
            <RadioButton
              {...optionProps}
              name={name}
              variant={variant}
              sizing={sizing}
              disabled={disabled}
              hasError={!!error}
              onChange={onChange}
              onBlur={onBlur}
              asset={asset}
              {...(onChange && {
                checked: checkedOption === optionProps.value,
              })}
            />
          </div>
        ))}
      </div>
    </fieldset>
  )
}
