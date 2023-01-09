import React, { ForwardedRef } from 'react'

import { Button } from 'ui-kit/Button'
import { ButtonVariant, SharedButtonProps } from 'ui-kit/Button/types'

export interface ISubmitButtonProps extends SharedButtonProps {
  className?: string
  disabled?: boolean
  isLoading?: boolean
  buttonRef?: ForwardedRef<HTMLButtonElement | null>
  onClick?(): void
  children?: React.ReactNode
}

const SubmitButton = ({
  children = 'Enregistrer',
  className,
  disabled = false,
  isLoading = false,
  buttonRef,
  onClick,
  ...buttonAttrs
}: ISubmitButtonProps): JSX.Element => (
  <Button
    className={className}
    disabled={disabled || isLoading}
    onClick={onClick}
    ref={buttonRef}
    type="submit"
    variant={ButtonVariant.PRIMARY}
    isLoading={isLoading}
    {...buttonAttrs}
  >
    {children}
  </Button>
)

export default SubmitButton
