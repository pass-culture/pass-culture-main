import classNames from 'classnames'
import { ForwardedRef, forwardRef, useEffect, useId, useRef } from 'react'

import styles from './Checkbox.module.scss'
import {
  CheckboxAsset,
  CheckboxAssetProps,
} from './CheckboxAsset/CheckboxAsset'

type CheckboxBaseProps = {
  /**
   * Classname applied to the `label` tag. Do not use this prop unless absolutely necessary.
   */
  className?: string
  /**
   * The label displayed next to the checkbox input.
   */
  label: string
  /**
   * Whether the checkbox is in an error state or not.
   */
  hasError?: boolean
  /**
   * Whether the checkbox is checked or not. The prop is mandatory, even when the ref is passed as prop, so that the input container styles are updated when the status changes.
   */
  checked: boolean
  /**
   * Whether the checkbox is partially checked or not.
   */
  indeterminate?: boolean
  /**
   * Whether the checkbox is disabled or not.
   */
  disabled?: boolean
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  onBlur?: (e: React.ChangeEvent<HTMLInputElement>) => void
  /**
   * Name of the input checkbox. Not necessary unless using a form library that relies on the name of the element.
   */
  name?: string
}

export type CheckboxProps = CheckboxBaseProps &
  (
    | {
        variant?: 'default'
        description?: never
        asset?: never
        collapsed?: never
        sizing?: 'hug' | 'fill'
      }
    | {
        variant: 'detailed'
        /**
         * Description test displayed under the checkbox label.
         */
        description?: string
        /**
         * Asset element displayed on the right of the checkbox.
         */
        asset?: CheckboxAssetProps
        /**
         * Content collapsed, displayed under the checkbox input when the checkbox is checked.
         */
        collapsed?: React.ReactNode
        /**
         * Display for the checkbox container. If `hug`, the width of the checkbox fits its content. If `fill` the checkbox takes all the available space.
         */
        sizing?: 'hug' | 'fill'
      }
  )

export const Checkbox = forwardRef(
  (
    {
      className,
      label,
      variant = 'default',
      description,
      asset,
      collapsed,
      sizing = collapsed ? 'fill' : 'hug',
      hasError,
      checked,
      indeterminate,
      disabled,
      onChange,
      onBlur,
      name,
    }: CheckboxProps,
    ref?: ForwardedRef<HTMLInputElement>
  ) => {
    const inputId = useId()
    const innerRef = useRef<HTMLInputElement | null>(null)

    useEffect(() => {
      if (innerRef.current) {
        innerRef.current.indeterminate = indeterminate ?? false
      }
    }, [indeterminate])

    return (
      <div
        className={classNames(
          styles['checkbox'],
          {
            [styles[variant]]: variant,
            [styles['checked']]: checked,
            [styles['indeterminate']]: indeterminate,
            [styles['disabled']]: disabled,
            [styles['has-error']]: hasError,
            [styles['has-collapsed-content']]: Boolean(collapsed),
          },
          styles[sizing]
        )}
      >
        <label
          className={classNames(styles['checkbox-label'], className)}
          htmlFor={inputId}
          aria-invalid={Boolean(hasError)}
        >
          <input
            className={styles['checkbox-input']}
            type="checkbox"
            id={inputId}
            ref={(e) => {
              //  The ref could be a ref callback function or a ref object
              if (ref instanceof Function) {
                ref(e)
              } else if (ref) {
                ref.current = e
              }

              innerRef.current = e
            }}
            checked={checked}
            disabled={disabled}
            onChange={onChange}
            onBlur={onBlur}
            name={name}
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
        {collapsed && (checked || indeterminate) && (
          <div className={styles['checkbox-collapsed-content']}>
            {collapsed}
          </div>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'
