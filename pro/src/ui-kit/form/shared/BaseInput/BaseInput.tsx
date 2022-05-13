import React, { ForwardedRef, forwardRef } from 'react'

import cn from 'classnames'
import styles from './BaseInput.module.scss'

interface IBaseInputProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  className?: string
  hasError?: boolean
  RightIcon?: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}

const BaseInput = forwardRef(
  (
    { className, hasError, name, RightIcon, ...props }: IBaseInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element =>
    !RightIcon ? (
      <input
        {...props}
        aria-invalid={hasError}
        className={cn(
          styles['base-input'],
          {
            [styles['has-error']]: hasError,
          },
          className
        )}
        id={name}
        name={name}
        ref={ref}
      />
    ) : (
      <div className={styles['base-input-wrapper']}>
        <input
          {...props}
          aria-invalid={hasError}
          className={cn(
            styles['base-input'],
            styles['base-input-with-right-icon'],
            {
              [styles['has-error']]: hasError,
            },
            className
          )}
          name={name}
          ref={ref}
        />
        <span className={styles['base-input-right-icon']}>
          <RightIcon />
        </span>
      </div>
    )
)

BaseInput.displayName = 'BaseInput'
export default BaseInput
