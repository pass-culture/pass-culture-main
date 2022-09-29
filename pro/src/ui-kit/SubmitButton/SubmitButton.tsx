import cx from 'classnames'
import React, { ForwardedRef } from 'react'

import { ReactComponent as SpinnerIcon } from './assets/loader.svg'
import styles from './SubmitButton.module.scss'

interface ISubmitButtonProps {
  className?: string
  disabled?: boolean
  isLoading?: boolean
  buttonRef?: ForwardedRef<HTMLButtonElement | null>
  onClick?(): void
  children?: React.ReactNode
  testId?: string
}

const SubmitButton = ({
  children = 'Enregistrer',
  className,
  disabled = false,
  isLoading = false,
  buttonRef,
  onClick,
  testId,
}: ISubmitButtonProps): JSX.Element => (
  <button
    className={cx(
      'primary-button',
      'loading-spinner',
      styles.submitButton,
      className
    )}
    disabled={disabled || isLoading}
    onClick={onClick}
    ref={buttonRef}
    type="submit"
    data-testid={testId ?? null}
  >
    {isLoading ? <SpinnerIcon /> : children}
  </button>
)

export default SubmitButton
