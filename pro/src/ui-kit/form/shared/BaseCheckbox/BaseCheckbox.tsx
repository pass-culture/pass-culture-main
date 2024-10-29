import cn from 'classnames'
import { useId, useRef, ForwardedRef, forwardRef, useEffect } from 'react'

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
  icon?: string
  withBorder?: boolean
  ref?: React.Ref<HTMLInputElement>
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
    }, [innerRef, partialCheck])

    return (
      <div
        className={cn(
          styles['base-checkbox'],
          {
            [styles['with-border']]: withBorder,
            [styles['has-error']]: hasError,
            [styles['is-disabled']]: props.disabled,
          },
          className
        )}
      >
        <span
          className={cn(styles['base-checkbox-label-row'], {
            [styles['base-checkbox-label-row-with-description']]:
              Boolean(description),
          })}
        >
          <input
            ref={partialCheck ? innerRef : forwardedRef}
            aria-invalid={hasError}
            {...(ariaDescribedBy
              ? { 'aria-describedby': ariaDescribedBy }
              : {})}
            type="checkbox"
            {...props}
            className={styles['base-checkbox-input']}
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
          <span
            className={cn(styles['base-checkbox-label'], {
              'visually-hidden': Boolean(exceptionnallyHideLabelDespiteA11y),
              [styles['base-checkbox-label-with-description']]:
                Boolean(description),
            })}
          >
            <label htmlFor={id}>{label}</label>
            {description && (
              <span className={styles['base-checkbox-description']}>
                {description}
              </span>
            )}
          </span>
        </span>
      </div>
    )
  }
)

BaseCheckbox.displayName = 'BaseCheckbox'
