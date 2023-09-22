import React, { ForwardedRef } from 'react'

import { Button } from 'ui-kit/Button'
import { ButtonVariant, SharedButtonProps } from 'ui-kit/Button/types'

export interface SubmitButtonProps extends SharedButtonProps {
  className?: string
  disabled?: boolean
  isLoading?: boolean
  buttonRef?: ForwardedRef<HTMLButtonElement | null>
  onClick?(): void
  onBlur?(): void
  onMouseDown?(e: React.MouseEvent): void
  children?: React.ReactNode
  type?: 'submit' | 'button'
}

const SubmitButton = ({
  children = 'Enregistrer',
  className,
  disabled = false,
  isLoading = false,
  buttonRef,
  onClick,
  onBlur,
  onMouseDown,
  type = 'submit',
  ...buttonAttrs
}: SubmitButtonProps): JSX.Element => (
  <Button
    className={className}
    disabled={disabled || isLoading}
    onClick={onClick}
    onBlur={onBlur}
    onMouseDown={onMouseDown}
    ref={buttonRef}
    type={type}
    variant={ButtonVariant.PRIMARY}
    isLoading={isLoading}
    {...buttonAttrs}
  >
    {children}
  </Button>
)

export default SubmitButton
