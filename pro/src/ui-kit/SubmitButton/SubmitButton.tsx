import cx from 'classnames'
import React, { FC } from 'react'

import { ReactComponent as SpinnerIcon } from './assets/loader.svg'
import styles from './SubmitButton.module.scss'

interface ISubmitButtonProps {
  className: string;
  disabled: boolean;
  isLoading: boolean;
  onClick(): void;
}

const SubmitButton: FC<ISubmitButtonProps> = ({ 
  children = 'Enregistrer',
  className,
  disabled = false,
  isLoading = false,
  onClick 
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
    type="submit"
  >
    {isLoading ? <SpinnerIcon /> : children}
  </button>
)


export default SubmitButton
