import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import styles from './RadioButton.module.scss'
import {
  RadioButtonAsset,
  RadioButtonAssetProps,
} from './RadioButtonAsset/RadioButtonAsset'

export type RadioButtonSizing = 'hug' | 'fill'

type RadioButtonBaseProps = {
  /** Label displayed next to the radio */
  label: string
  /** Name of the radio group */
  name: string
  /** Value of the radio input. It identifies a single radio input within a group. */
  value: string
  /** If the radio is selected */
  checked?: boolean
  /** Component size. If `hug` the input width matches its content. If `fill` the input takes all available space. */
  sizing?: RadioButtonSizing
  /** If the radio is disabled */
  disabled?: boolean
  /** If the radio is in an error state */
  hasError?: boolean
  /** Event handler for change */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  /** Event handler for blur */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

export type RadioButtonVariantProps = {
  variant?: 'default' | 'detailed'
  /**
   * Description text displayed under the checkbox label.
   */
  description?: string
  /**
   * Asset element displayed on the right of the checkbox.
   */
  asset?: RadioButtonAssetProps
  /**
   * Content collapsed, displayed under the checkbox input when the checkbox is checked.
   */
  collapsed?: React.ReactNode
}
export type RadioButtonProps = RadioButtonBaseProps & RadioButtonVariantProps

export const RadioButton = forwardRef(
  (
    {
      label,
      value,
      variant,
      sizing,
      description,
      collapsed,
      asset,
      disabled,
      hasError,
      checked,
      onChange,
      onBlur,
      name,
    }: RadioButtonProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const id = useId()

    const isVariantDetailed = variant === 'detailed'

    return (
      <>
        <div
          className={cn(styles['radio-button'], {
            [styles['sizing-fill']]: sizing === 'fill',
            [styles['variant-detailed']]: isVariantDetailed,
            [styles['is-collapsed']]: collapsed && checked,
            [styles['is-checked']]: checked,
            [styles['is-disabled']]: disabled,
            [styles['has-error']]: hasError,
          })}
        >
          <label htmlFor={id} className={styles['radio-button-label']}>
            <div className={styles['radio-button-left']}>
              <input
                type="radio"
                value={value}
                className={styles[`radio-button-input`]}
                id={id}
                ref={ref}
                onChange={onChange}
                onBlur={onBlur}
                disabled={disabled}
                name={name}
                checked={checked}
                aria-invalid={hasError}
              />
              <div>
                {label}
                {description && isVariantDetailed && (
                  <p className={styles['description']}>{description}</p>
                )}
              </div>
            </div>
            {asset && isVariantDetailed && (
              <RadioButtonAsset
                {...asset}
                className={cn(styles['radio-asset'], {
                  [styles[asset.variant]]: asset.variant,
                })}
              />
            )}
          </label>
          {collapsed && isVariantDetailed && checked && (
            <div className={styles['collapsed']}>{collapsed}</div>
          )}
        </div>
      </>
    )
  }
)
RadioButton.displayName = 'RadioButton'
