import cn from 'classnames'
import { useField } from 'formik'
import React, { useId } from 'react'

import { Tooltip } from 'ui-kit/Tooltip/Tooltip'
import { useTooltipProps } from 'ui-kit/Tooltip/useTooltipProps'

import styles from './IconRadio.module.scss'

interface IconRadioProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  label: string
  icon: string | JSX.Element
  hasError?: boolean
  className?: string
}

export const IconRadio = ({
  name,
  value,
  label,
  icon,
  hasError,
  className,
  ...props
}: IconRadioProps): JSX.Element => {
  const id = useId()
  const [field] = useField({ name, value, type: 'radio' })

  const { isTooltipHidden, ...tooltipProps } = useTooltipProps({})

  return (
    <a
      className={cn(
        styles['icon-radio'],
        { [styles['icon-radio-checked']]: field.checked },
        { [styles['icon-radio-disabled']]: props.disabled },
        className
      )}
      {...tooltipProps}
    >
      <label
        htmlFor={id}
        className={cn(styles['icon-radio-label'], {
          [styles['has-error']]: hasError,
          [styles['icon-radio-label-checked']]: field.checked,
          [styles['icon-radio-label-disabled']]: props.disabled,
        })}
      >
        <input
          {...field}
          type="radio"
          {...props}
          className={styles[`icon-radio-input`]}
          aria-invalid={hasError}
          id={id}
          checked={field.checked}
          disabled={props.disabled}
        />

        <Tooltip
          content={label}
          visuallyHidden={isTooltipHidden}
          tooltipContainerClassName={styles['icon-radio-label-tooltip']}
        >
          <span aria-hidden={true} className={styles['icon-radio-label-icon']}>
            {icon}
          </span>
        </Tooltip>
      </label>
    </a>
  )
}
