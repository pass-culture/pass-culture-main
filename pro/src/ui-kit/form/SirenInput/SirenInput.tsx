import { useField } from 'formik'
import React, { useEffect } from 'react'

import { humanizeSiren } from 'core/Offerers/utils'

import TextInput from '../TextInput'

const formatSiren = (siren: string) => {
  const lastChar = siren.charAt(siren.length - 1)
  // remove character when it's not a number
  // this way we're sure that this field only accept number
  if (lastChar && isNaN(Number(lastChar))) {
    return siren.slice(0, -1)
  }
  return humanizeSiren(siren)
}

interface ISirenInputProps {
  label: string
  name?: string
  placeholder?: string
  onValidSiren: (value: string) => void
}

const SirenInput = ({
  label,
  name = 'siren',
  placeholder = '123456789',
  onValidSiren,
}: ISirenInputProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name })
  const { setValue } = helpers
  useEffect(() => {
    setValue(formatSiren(field.value))
    if (!meta.error && meta.touched) {
      onValidSiren(field.value)
    }
  }, [meta.touched, meta.error, field.value])

  return (
    <TextInput
      label={label}
      maxLength={11}
      name={name}
      placeholder={placeholder}
      type="text"
    />
  )
}

export default SirenInput
