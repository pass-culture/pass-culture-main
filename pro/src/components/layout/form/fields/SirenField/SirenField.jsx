import PropTypes from 'prop-types'
import React from 'react'
import { Field } from 'react-final-form'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { humanizeSiren, unhumanizeSiren } from 'core/Offerers/utils'

import validate from './validate'

const formatSiren = value => {
  // remove character when when it's not a number
  // this way we're sure that this field only accept number
  if (value && isNaN(Number(value))) {
    return value.slice(0, -1)
  }
  return humanizeSiren(value)
}

const SirenField = ({ label }) => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    parse={unhumanizeSiren}
    validate={validate}
  >
    {({ input, meta }) => {
      return (
        <TextInput
          error={meta.modified && meta.error ? meta.error : null}
          label={label}
          maxLength="11"
          name="siren"
          onChange={input.onChange}
          placeholder="123456789"
          sublabel="obligatoire"
          value={input.value}
        />
      )
    }}
  </Field>
)

SirenField.defaultProps = {
  label: 'SIREN',
}

SirenField.propTypes = {
  label: PropTypes.string,
}

export default SirenField
