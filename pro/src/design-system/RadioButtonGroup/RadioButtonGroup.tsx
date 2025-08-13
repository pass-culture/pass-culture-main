import cn from 'classnames'
import { type ElementType, useId } from 'react'

import {
  RadioButton,
  type RadioButtonProps,
  type RadioButtonSizing,
  type RadioButtonVariantProps,
} from '@/design-system/RadioButton/RadioButton'
import fullErrorIcon from '@/icons/full-error.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButtonGroup.module.scss'

export type RadioButtonGroupProps<
  N extends string,
  V extends RadioButtonVariantProps,
  S extends RadioButtonSizing,
  D extends boolean,
  onChange = (event: React.ChangeEvent<HTMLInputElement>) => void,
  onBlur = (event: React.FocusEvent<HTMLInputElement>) => void,
> = {
  /** Name of the radio button group, binding all radio buttons together */
  name: N
  /** Label for the radio button group */
  label: string
  /** List of options as radio buttons */
  options: Array<
    Omit<RadioButtonProps, 'name'> & {
      name?: N
      sizing?: S
      disabled?: D
      onChange?: onChange
      onBlur?: onBlur
    } & V
  >
  /** Tag for the label, defaults to 'span', can be 'h1', 'h2', etc. */
  labelTag?: ElementType
  /** Description for the radio button group */
  description?: string
  /** Error message for the radio button group */
  error?: string
  /** Variant of the radio buttons (applied to all), defaults to 'default' */
  variant?: V['variant']
  /** Sizing of the radio buttons (applied to all), defaults to 'fill' */
  sizing?: S
  /** Asset of the radio buttons (applied to all), displayed when variant is 'detailed' */
  asset?: V['asset']
  /** Display style of the radio button group, defaults to 'vertical' */
  display?: 'horizontal' | 'vertical'
  /** Selected option, required if the group is non-controlled */
  checkedOption?: string
  /** Custom CSS class for the radio button group */
  className?: string
  /** Custom CSS class for the label */
  labelClassName?: string
  /** If the radio button group is disabled, making all options unselectable */
  disabled?: D
  /** Event handler for change */
  onChange?: onChange
  /** Event handler for blur */
  onBlur?: onBlur
  /** Whether the checkbox is required or not */
  required?: boolean
  /** Whether the required asterisk is displayed or not */
  asterisk?: boolean
  /** Allow options to be an array with none, or a single element - exception case: CollectiveOfferSelectionDuplication */
  allowSingleOrNoneOption?: boolean
}

export const RadioButtonGroup = ({
  name,
  label,
  options,
  labelTag: LabelTag = 'span',
  description,
  error,
  variant = 'default',
  sizing = 'fill',
  display = 'vertical',
  disabled = false,
  checkedOption,
  className,
  labelClassName,
  asset,
  onChange,
  onBlur,
  required,
  asterisk = true,
  allowSingleOrNoneOption,
}: RadioButtonGroupProps<
  string,
  RadioButtonVariantProps,
  RadioButtonSizing,
  boolean,
  (event: React.ChangeEvent<HTMLInputElement>) => void,
  (event: React.FocusEvent<HTMLInputElement>) => void
>): JSX.Element => {
  const labelId = useId()
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = `${error ? errorId : ''}${description ? ` ${descriptionId}` : ''}`

  if (!allowSingleOrNoneOption && options.length < 2) {
    throw new Error('RadioButtonGroup requires at least two options.')
  }

  // Ensure all options have distinct values, which is natural
  // for radio buttons but also a requirement since they are used as unique keys.
  const values = options.map((option) => option.value)
  if (new Set(values).size !== values.length) {
    throw new Error('RadioButtonGroup options must have unique values.')
  }

  return (
    <div
      role="radiogroup"
      aria-labelledby={labelId}
      aria-describedby={describedBy}
      aria-required={required}
      aria-invalid={!!error}
      className={cn(styles['radio-button-group'], className)}
      data-testid={`wrapper-${name}`}
    >
      <div className={styles['radio-button-group-header']}>
        <LabelTag
          id={labelId}
          className={cn(
            styles[`radio-button-group-label-${LabelTag}`],
            labelClassName
          )}
        >
          {label}
          {required && asterisk ? ' *' : ''}
        </LabelTag>
        <span
          id={descriptionId}
          className={styles['radio-button-group-description']}
          // Description might change based on selection,
          // so an aria-live is needed to announce changes.
          aria-live="polite"
        >
          {description}
        </span>
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
          <RadioButton
            key={optionProps.value}
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
        ))}
      </div>
    </div>
  )
}
