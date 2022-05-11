import React, { useEffect } from 'react'

import TextInput from '../TextInput'
import { humanizeSiren } from 'core/Offerers/utils'
import { useField } from 'formik'

const formatSiren = (value: string) => {
  // remove character when when it's not a number
  // this way we're sure that this field only accept number
  if (value && isNaN(Number(value))) {
    return value.slice(0, -1)
  }
  return humanizeSiren(value)
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
    if (!meta.touched) return
    if (!meta.error) {
      setValue(formatSiren(field.value))
      onValidSiren(field.value)
    }
  }, [meta.touched, meta.error])

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
