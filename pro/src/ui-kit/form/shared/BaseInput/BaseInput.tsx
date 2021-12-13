import cn from 'classnames'
import React from 'react'

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

const BaseInput = ({
  className,
  hasError,
  name,
  RightIcon,
  ...props
}: IBaseInputProps): JSX.Element =>
  !RightIcon ? (
    <input
      {...props}
      className={cn(
        styles['base-input'],
        {
          [styles['has-error']]: hasError,
        },
        className
      )}
      id={name}
    />
  ) : (
    <div className={styles['base-input-wrapper']}>
      <input
        {...props}
        className={cn(
          styles['base-input'],
          styles['base-input-with-right-icon'],
          {
            [styles['has-error']]: hasError,
          },
          className
        )}
      />
      <span className={styles['base-input-right-icon']}>
        <RightIcon />
      </span>
    </div>
  )

export default BaseInput
