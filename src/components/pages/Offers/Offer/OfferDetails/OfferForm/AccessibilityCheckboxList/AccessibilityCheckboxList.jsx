import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { CheckboxInput } from 'components/layout/inputs/CheckboxInput/CheckboxInput'
import InputError from 'components/layout/inputs/Errors/InputError'
import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'

const autoFillValues = function (formValues, field, value) {
  let disabilityCompliantValues = {
    noDisabilityCompliant: formValues.noDisabilityCompliant,
    audioDisabilityCompliant: formValues.audioDisabilityCompliant,
    mentalDisabilityCompliant: formValues.mentalDisabilityCompliant,
    motorDisabilityCompliant: formValues.motorDisabilityCompliant,
    visualDisabilityCompliant: formValues.visualDisabilityCompliant,
  }

  disabilityCompliantValues[field] = value

  if (field === 'noDisabilityCompliant') {
    if (disabilityCompliantValues[field]) {
      disabilityCompliantValues.audioDisabilityCompliant = false
      disabilityCompliantValues.mentalDisabilityCompliant = false
      disabilityCompliantValues.motorDisabilityCompliant = false
      disabilityCompliantValues.visualDisabilityCompliant = false
    } else {
      const hasNoDisabilityCompliance = ![
        disabilityCompliantValues.audioDisabilityCompliant,
        disabilityCompliantValues.mentalDisabilityCompliant,
        disabilityCompliantValues.motorDisabilityCompliant,
        disabilityCompliantValues.visualDisabilityCompliant,
      ].includes(true)
      if (hasNoDisabilityCompliance) {
        disabilityCompliantValues[field] = true
      }
    }
  } else {
    if (Object.values(disabilityCompliantValues).includes(true)) {
      disabilityCompliantValues.noDisabilityCompliant = false
    } else {
      disabilityCompliantValues.noDisabilityCompliant = true
    }
  }

  return disabilityCompliantValues
}

const AccessibilityCheckboxList = ({ onChange, formValues, isInError, isDisabled, readOnly }) => {
  const handleChange = useCallback(
    event => {
      onChange(autoFillValues(formValues, event.target.name, event.target.checked))
    },
    [formValues, onChange]
  )

  return (
    <>
      <CheckboxInput
        SvgElement={VisualDisabilitySvg}
        checked={formValues.visualDisabilityCompliant}
        disabled={readOnly}
        isInError={isInError}
        isLabelDisable={isDisabled}
        label="Visuel"
        name="visualDisabilityCompliant"
        onChange={handleChange}
      />
      <CheckboxInput
        SvgElement={MentalDisabilitySvg}
        checked={formValues.mentalDisabilityCompliant}
        disabled={readOnly}
        isInError={isInError}
        isLabelDisable={isDisabled}
        label="Psychique ou cognitif"
        name="mentalDisabilityCompliant"
        onChange={handleChange}
      />
      <CheckboxInput
        SvgElement={MotorDisabilitySvg}
        checked={formValues.motorDisabilityCompliant}
        disabled={readOnly}
        isInError={isInError}
        isLabelDisable={isDisabled}
        label="Moteur"
        name="motorDisabilityCompliant"
        onChange={handleChange}
      />
      <CheckboxInput
        SvgElement={AudioDisabilitySvg}
        checked={formValues.audioDisabilityCompliant}
        disabled={readOnly}
        isInError={isInError}
        isLabelDisable={isDisabled}
        label="Auditif"
        name="audioDisabilityCompliant"
        onChange={handleChange}
      />
      <CheckboxInput
        checked={formValues.noDisabilityCompliant}
        disabled={readOnly}
        isInError={isInError}
        isLabelDisable={isDisabled}
        label="Non accessible"
        name="noDisabilityCompliant"
        onChange={handleChange}
      />

      {isInError && (
        <InputError>
          Vous devez cocher l’une des options ci-dessus
        </InputError>
      )}
    </>
  )
}

AccessibilityCheckboxList.defaultProps = {
  isDisabled: false,
  isInError: false,
  readOnly: false,
}

AccessibilityCheckboxList.propTypes = {
  formValues: PropTypes.shape().isRequired,
  isDisabled: PropTypes.bool,
  isInError: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  readOnly: PropTypes.bool,
}

export default AccessibilityCheckboxList
