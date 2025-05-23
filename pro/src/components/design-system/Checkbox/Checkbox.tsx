import classNames from 'classnames'
import { ForwardedRef, forwardRef, useEffect, useId, useRef } from 'react'

import styles from './Checkbox.module.scss'
import {
  CheckboxAsset,
  CheckboxAssetProps,
} from './CheckboxAsset/CheckboxAsset'

export type CheckboxVariant = 'default' | 'detailed'

export type CheckboxBaseProps = {
  label: string
  variant?: CheckboxVariant
  hasError?: boolean
  checked?: boolean
  indeterminate?: boolean
  disabled?: boolean
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  onBlur?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export type CheckboxProps = CheckboxBaseProps &
  (
    | {
        variant: 'default'
        description?: never
        asset?: never
        collapsedContent?: never
        display?: never
      }
    | {
        variant: 'detailed'
        description?: string
        asset?: CheckboxAssetProps
        collapsedContent?: React.ReactNode
        display?: 'fit' | 'full'
      }
  )

export const Checkbox = forwardRef(
  (
    {
      label,
      variant = 'default',
      description,
      asset,
      collapsedContent,
      display = 'fit',
      hasError,
      checked,
      indeterminate,
      disabled,
      onChange,
      onBlur,
    }: CheckboxProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const inputId = useId()
    const innerRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
      if (innerRef.current) {
        innerRef.current.indeterminate = indeterminate ?? false
      }
    }, [indeterminate])

    if (variant === 'detailed' && collapsedContent) {
      display = 'full'
    }

    return (
      <div
        className={classNames(styles['checkbox'], {
          [styles[variant]]: variant,
          [styles['checked']]: checked,
          [styles['disabled']]: disabled,
          [styles['has-error']]: hasError,
          [styles['has-collapsed-content']]: Boolean(collapsedContent),
          [styles[display]]: display,
        })}
      >
        <label className={styles['checkbox-label']} htmlFor={inputId}>
          <input
            className={styles['checkbox-input']}
            type="checkbox"
            id={inputId}
            ref={ref ?? innerRef}
            checked={checked}
            disabled={disabled}
            onChange={onChange}
            onBlur={onBlur}
          />
          <div className={styles['checkbox-label-row']}>
            <div className={styles['checkbox-label-row-left']}>
              {label}
              {description && (
                <p className={styles['checkbox-description']}>{description}</p>
              )}
            </div>
            {asset && (
              <div className={styles['checkbox-label-row-right']}>
                <CheckboxAsset
                  {...asset}
                  className={classNames(styles['checkbox-asset'], {
                    [styles[asset.variant]]: asset.variant,
                  })}
                />
              </div>
            )}
          </div>
        </label>
        {collapsedContent && (
          <div className={styles['checkbox-collapsed-content']}>
            {collapsedContent}
          </div>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'
