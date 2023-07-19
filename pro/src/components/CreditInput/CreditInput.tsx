import React, { FunctionComponent, useCallback } from 'react'

import TextInput from 'ui-kit/form/TextInput/TextInput'

interface CreditInputProps {
  credit: string
  updateCredit: (credit: string) => void
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void
  extraClassName?: string
}

export const CreditInput: FunctionComponent<CreditInputProps> = ({
  credit,
  updateCredit,
  onKeyDown,
  extraClassName = '',
}) => {
  const onCreditChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newCredit = event.target.value
      updateCredit(newCredit)
    },
    [updateCredit]
  )

  return (
    <TextInput
      countCharacters
      className={extraClassName}
      label="Crédit image"
      maxLength={255}
      name="credit"
      onChange={onCreditChange}
      onKeyDown={onKeyDown}
      placeholder="Photographe..."
      required={false}
      type="text"
      value={credit}
    />
  )
}
