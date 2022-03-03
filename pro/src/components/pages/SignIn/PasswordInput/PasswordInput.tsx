import React, { useState } from 'react'

import TextInputWithIcon from 'components/layout/inputs/TextInputWithIcon/TextInputWithIcon'

interface IPasswordInputProps {
  onChange: (newValue: string) => void
  value: string
}

const PasswordInput = ({
  onChange,
  value,
}: IPasswordInputProps): JSX.Element => {
  const [isPasswordHidden, setIsPasswordHidden] = useState<boolean>(true)
  const handleToggleHidden = (e: React.MouseEvent<HTMLInputElement>) => {
    e.preventDefault()
    setIsPasswordHidden(previousIsPasswordHidden => !previousIsPasswordHidden)
  }

  const handleOnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event?.target.value)
  }

  return (
    <TextInputWithIcon
      icon={isPasswordHidden ? 'ico-eye-close' : 'ico-eye-open'}
      iconAlt={
        isPasswordHidden ? 'Afficher le mot de passe' : 'Cacher le mot de passe'
      }
      label="Mot de passe"
      name="password"
      onChange={handleOnChange}
      onIconClick={handleToggleHidden}
      placeholder="Mot de passe"
      required
      type={isPasswordHidden ? 'password' : 'text'}
      value={value}
    />
  )
}

export default PasswordInput
