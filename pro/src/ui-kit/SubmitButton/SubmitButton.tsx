import cx from 'classnames'
import React, { FC, ForwardedRef } from 'react'

import { ReactComponent as SpinnerIcon } from './assets/loader.svg'
import styles from './SubmitButton.module.scss'

interface ISubmitButtonProps {
  className?: string
  disabled?: boolean
  isLoading: boolean
  buttonRef?: ForwardedRef<HTMLButtonElement | null>
  onClick?(): void
  children?: React.ReactNode
}

const SubmitButton: FC<ISubmitButtonProps> = ({
  children = 'Enregistrer',
  className,
  disabled = false,
  isLoading = false,
  buttonRef,
  onClick,
}) => (
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
  >
    {isLoading ? <SpinnerIcon /> : children}
  </button>
)

export default SubmitButton
