import cn from 'classnames'
import { useId, useRef, useEffect, ForwardedRef, forwardRef } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseCheckbox.module.scss'

export enum PartialCheck {
  CHECKED = 'checked',
  PARTIAL = 'partial',
  UNCHECKED = 'unchecked',
}

export interface BaseCheckboxProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string | React.ReactNode
  hasError?: boolean
  className?: string
  inputClassName?: string
  labelClassName?: string
  icon?: string
  withBorder?: boolean
  partialCheck?: boolean
  exceptionnallyHideLabelDespiteA11y?: boolean
  description?: string
  ariaDescribedBy?: string
}

export const BaseCheckbox = forwardRef(
  (
    {
      label,
      hasError,
      className,
      inputClassName,
      labelClassName,
      icon,
      withBorder,
      partialCheck,
      exceptionnallyHideLabelDespiteA11y,
      description,
      ariaDescribedBy,
      ...props
    }: BaseCheckboxProps,
    forwardedRef: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const innerRef = useRef<HTMLInputElement>(null)
    const id = useId()

    useEffect(() => {
      if (innerRef.current) {
        innerRef.current.indeterminate = partialCheck ?? false
      }
    }, [partialCheck])

    const labelClasses = cn(
      styles['base-checkbox-label'],
      {
        [styles['visually-hidden']]: exceptionnallyHideLabelDespiteA11y,
      },
      labelClassName
    )
    const containerClasses = cn(styles['base-checkbox'], className, {
      [styles['with-border']]: withBorder,
      [styles['has-error']]: hasError,
      [styles['is-disabled']]: props.disabled,
    })

    return (
      <div className={containerClasses}>
        <span className={styles['base-checkbox-label-row']}>
          <input
            ref={forwardedRef ?? innerRef}
            aria-invalid={hasError}
            {...(ariaDescribedBy && { 'aria-describedby': ariaDescribedBy })}
            type="checkbox"
            {...props}
            className={cn(styles['base-checkbox-input'], inputClassName)}
            id={id}
          />
          {icon && (
            <span className={styles['base-checkbox-icon']}>
              <SvgIcon
                src={icon}
                alt=""
                className={styles['base-checkbox-icon-svg']}
              />
            </span>
          )}
          <label className={labelClasses} htmlFor={id}>
            {label}
            {description && (
              <p className={styles['base-checkbox-description']}>
                {description}
              </p>
            )}
          </label>
        </span>
      </div>
    )
  }
)

BaseCheckbox.displayName = 'BaseCheckbox'
