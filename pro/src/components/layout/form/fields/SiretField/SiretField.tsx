import React, { useEffect } from 'react'
import { humanizeSiret, unhumanizeSiret } from 'core/Venue/utils'

import ReactTooltip from 'react-tooltip'
import TextField from 'components/layout/form/fields/TextField'
import { TooltipInvalidSiret } from './TooltipInvalidSiret'
import { TooltipValidSiret } from './TooltipValidSiret'
import siretApiValidate from './validators/siretApiValidate'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useField } from 'react-final-form'

interface ISiretFieldProps {
  label: string
  readOnly: boolean
  siren?: string
}

const SiretField = ({
  label = 'SIRET : ',
  readOnly = true,
  siren,
}: ISiretFieldProps): JSX.Element => {
  const isEntrepriseApiDisabled: boolean = useActiveFeature(
    'DISABLE_ENTERPRISE_API'
  )

  const siretFormField = useField('siret', {})
  const commentFormField = useField('comment', {})
  const haveInitialValue = ![null, undefined].includes(
    siretFormField.meta.initial
  )
  const siretValue = siretFormField.input.value
  const commentValue = commentFormField.input.value
  const isValid = !!siretValue && siretValue.length === 14

  let validate: ((siret: string) => Promise<string | undefined>) | null = null

  if (!(haveInitialValue || isEntrepriseApiDisabled)) {
    validate = (siret: string) => {
      if (siren && siret && !siret.startsWith(siren)) {
        return Promise.resolve(
          'Le code SIRET doit correspondre à un établissement de votre structure'
        )
      }
      return siretApiValidate(siret, commentValue)
    }
  }

  let tooltip: JSX.Element | null
  if (readOnly) {
    tooltip = null
  } else {
    tooltip = isValid ? <TooltipValidSiret /> : <TooltipInvalidSiret />
  }
  useEffect(() => {
    ReactTooltip.rebuild()
  }, [isValid])

  const formatSiret = (value: string): string => {
    // remove character when when it's not a number
    // this way we're sure that this field only accept number
    if (value && isNaN(Number(value))) {
      return value.slice(0, -1)
    }
    return humanizeSiret(value)
  }

  return (
    <TextField
      format={formatSiret}
      label={label}
      name="siret"
      parse={unhumanizeSiret}
      readOnly={readOnly}
      renderTooltip={() => tooltip}
      type="siret"
      validate={validate}
    />
  )
}

export default SiretField
