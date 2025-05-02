import cn from 'classnames'
import { ForwardedRef, forwardRef, useEffect, useId, useRef } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseCheckbox.module.scss'

export enum PartialCheck {
  CHECKED = 'checked',
  PARTIAL = 'partial',
  UNCHECKED = 'unchecked',
}

export enum CheckboxVariant {
  DEFAULT = 'default',
  BOX = 'box',
}

export interface BaseCheckboxProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string | React.ReactNode
  hasError?: boolean
  className?: string
  inputClassName?: string
  labelClassName?: string
  icon?: string
  variant?: CheckboxVariant
  partialCheck?: boolean
  exceptionnallyHideLabelDespiteA11y?: boolean
  description?: string
  ariaDescribedBy?: string
  childrenOnChecked?: JSX.Element
  shouldShowChildren?: boolean
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
      variant = CheckboxVariant.DEFAULT,
      partialCheck,
      exceptionnallyHideLabelDespiteA11y,
      description,
      ariaDescribedBy,
      childrenOnChecked,
      shouldShowChildren = false,
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

    const labelClasses = cn(styles['base-checkbox-label'], labelClassName)
    const containerClasses = cn(styles['base-checkbox'], className, {
      [styles['box-variant']]: variant === CheckboxVariant.BOX,
      [styles['has-error']]: hasError,
      [styles['is-disabled']]: props.disabled,
      [styles['is-checked']]: props.checked,
      [styles['has-children']]: childrenOnChecked,
    })

    return (
      <div className={containerClasses}>
        <div className={styles['base-checkbox-row']}>
          <span className={styles['base-checkbox-label-row']}>
            <label className={labelClasses} htmlFor={id}>
              <input
                aria-invalid={hasError}
                {...(ariaDescribedBy && {
                  'aria-describedby': ariaDescribedBy,
                })}
                type="checkbox"
                {...props}
                className={cn(styles['base-checkbox-input'], inputClassName)}
                id={id}
                ref={forwardedRef ?? innerRef}
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
              <div
                className={cn({
                  [styles['visually-hidden']]:
                    exceptionnallyHideLabelDespiteA11y,
                })}
              >
                {label}
                {description && (
                  <p className={styles['base-checkbox-description']}>
                    {description}
                  </p>
                )}
              </div>
            </label>
          </span>
        </div>
        <div>
          {(childrenOnChecked && props.checked) || shouldShowChildren ? (
            <div className={styles['base-checkbox-children-on-checked']}>
              {childrenOnChecked}
            </div>
          ) : null}
        </div>
      </div>
    )
  }
)

BaseCheckbox.displayName = 'BaseCheckbox'
