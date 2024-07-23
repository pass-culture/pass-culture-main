import cn from 'classnames'
import { useEffect, useId, useRef } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseCheckbox.module.scss'

export enum PartialCheck {
  CHECKED = 'checked',
  PARTIAL = 'partial',
  UNCHECKED = 'unchecked',
}

interface BaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | React.ReactNode
  hasError?: boolean
  className?: string
  icon?: string
  withBorder?: boolean
  ref?: React.Ref<HTMLInputElement>
  partialCheck?: boolean
  exceptionnallyHideLabelDespiteA11y?: boolean
  description?: string
}

export const BaseCheckbox = ({
  label,
  hasError,
  className,
  icon,
  withBorder,
  partialCheck,
  exceptionnallyHideLabelDespiteA11y,
  description,
  ...props
}: BaseCheckboxProps): JSX.Element => {
  const checkboxRef = useRef<HTMLInputElement>(null)
  const id = useId()

  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = partialCheck ?? false
    }
  }, [checkboxRef, partialCheck])

  return (
    <label
      className={cn(
        styles['base-checkbox'],
        {
          [styles['with-border']]: withBorder,
          [styles['has-error']]: hasError,
          [styles['is-disabled']]: props.disabled,
        },
        className
      )}
      htmlFor={id}
    >
      <span
        className={cn(styles['base-checkbox-label-row'], {
          [styles['base-checkbox-label-row-with-description']]:
            Boolean(description),
        })}
      >
        <input
          ref={checkboxRef}
          aria-invalid={hasError}
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
            ['visually-hidden']: Boolean(exceptionnallyHideLabelDespiteA11y),
            [styles['base-checkbox-label-with-description']]:
              Boolean(description),
          })}
        >
          {label}
          {description && (
            <span className={styles['base-checkbox-description']}>
              {description}
            </span>
          )}
        </span>
      </span>
    </label>
  )
}
