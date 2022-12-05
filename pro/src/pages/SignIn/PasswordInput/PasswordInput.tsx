import React, { useState } from 'react'

import { IcoEyeClose, IcoEyeOpen } from 'icons'
import TextInputWithIcon from 'ui-kit/form_raw/TextInputWithIcon/TextInputWithIcon'

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
      icon={isPasswordHidden ? <IcoEyeClose /> : <IcoEyeOpen />}
      label="Mot de passe"
      name="password"
      onChange={handleOnChange}
      onIconClick={handleToggleHidden}
      placeholder="Votre mot de passe"
      required
      type={isPasswordHidden ? 'password' : 'text'}
      value={value}
    />
  )
}

export default PasswordInput
