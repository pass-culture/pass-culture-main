import React from 'react'
import { Field } from 'react-final-form'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { humanizeSiren, unhumanizeSiren } from 'core/Offerers/utils'

import validate from './validate'

// const required = value => {
//   return value ? undefined : 'Ce champ est obligatoire'
// }

// const mustHaveTheProperLength = value => {
//   return value.length < 9 ? 'SIREN trop court' : undefined
// }

// const simpleMemoize = fn => {
//   let lastArg
//   let lastResult
//   return arg => {
//     if (arg !== lastArg) {
//       lastArg = arg
//       lastResult = fn(arg)
//     }
//     return lastResult
//   }
// }

// export const existsInINSEERegistry = simpleMemoize(async value => {
//   value = removeWhitespaces(value)
//   const response = await getSirenDataAdapter(value)
//   return response.isOk ? undefined : response.message
// })

const formatSiren = value => {
  // remove character when when it's not a number
  // this way we're sure that this field only accept number
  if (value && isNaN(Number(value))) {
    return value.slice(0, -1)
  }
  return humanizeSiren(value)
}

const SirenField = ({ label = 'SIREN', description }) => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    parse={unhumanizeSiren}
    validate={validate}
  >
    {({ input, meta }) => {
      return (
        <>
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
          {description && (
            <span className="field-siren-value">{description}</span>
          )}
        </>
      )
    }}
  </Field>
)

export default SirenField
