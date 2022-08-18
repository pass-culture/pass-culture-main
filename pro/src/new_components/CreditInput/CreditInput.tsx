import React, { FunctionComponent, useCallback } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'

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
      extraClassName={extraClassName}
      label="Crédit image"
      maxLength={255}
      name="image-credit-input"
      onChange={onCreditChange}
      onKeyDown={onKeyDown}
      placeholder="Photographe..."
      required={false}
      subLabel="Optionnel"
      type="text"
      value={credit}
    />
  )
}
