import React, { ForwardedRef } from 'react'

import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, SharedButtonProps } from 'ui-kit/Button/types'

export interface SubmitButtonProps
  extends SharedButtonProps,
    React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean
  buttonRef?: ForwardedRef<HTMLButtonElement | null>
}

export const SubmitButton = ({
  children = 'Enregistrer',
  disabled = false,
  isLoading = false,
  buttonRef,
  type = 'submit',
  ...buttonAttrs
}: SubmitButtonProps): JSX.Element => (
  <Button
    disabled={disabled || isLoading}
    ref={buttonRef}
    type={type}
    variant={ButtonVariant.PRIMARY}
    isLoading={isLoading}
    {...buttonAttrs}
  >
    {children}
  </Button>
)
