import cn from 'classnames'
import { useEffect, useRef } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './BaseCheckbox.module.scss'

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
}

export const BaseCheckbox = ({
  label,
  hasError,
  className,
  icon,
  withBorder,
  partialCheck,
  exceptionnallyHideLabelDespiteA11y,
  ...props
}: BaseCheckboxProps): JSX.Element => {
  const checkboxRef = useRef<HTMLInputElement>(null)

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
    >
      <span className={styles['base-checkbox-label-row']}>
        <input
          ref={checkboxRef}
          aria-invalid={hasError}
          type="checkbox"
          {...props}
          className={styles['base-checkbox-input']}
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
          })}
        >
          {label}
        </span>
      </span>
    </label>
  )
}
