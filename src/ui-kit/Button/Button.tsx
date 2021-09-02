/* eslint-disable react/button-has-type */
import cx from 'classnames'
import React from 'react'

import styles from './Button.module.scss'

interface IButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  type: "submit" | "reset" | "button";
  addClass?: string;
}

const Button: React.FC<IButtonProps> = ({
  children,
  type,
  addClass,
  ...rest 
}) => (
  <button
    className={cx(styles.button, addClass)}
    type={type}
    {...rest}
  >
    {children}
  </button>
)

export default Button