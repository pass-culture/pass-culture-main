import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import CheckboxInput from 'components/layout/inputs/CheckboxInput'
import InputError from 'components/layout/inputs/Errors/InputError'
import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'

import {
  checkHasNoDisabilityCompliance,
  getAccessibilityValues,
} from './helpers'

const autoFillValues = function (formValues, field, value) {
  let noDisabilityCompliant = formValues.noDisabilityCompliant
  let disabilityCompliantValues = getAccessibilityValues(formValues)
  // normalize null value as false
  disabilityCompliantValues = Object.keys(disabilityCompliantValues).reduce(
    (acc, field) => ({ ...acc, [field]: !!disabilityCompliantValues[field] }),
    {}
  )

  if (field === 'noDisabilityCompliant') {
    noDisabilityCompliant = value

    if (noDisabilityCompliant) {
      disabilityCompliantValues = Object.keys(disabilityCompliantValues).reduce(
        (acc, field) => ({ ...acc, [field]: false }),
        {}
      )
    } else if (!Object.values(disabilityCompliantValues).includes(true)) {
      noDisabilityCompliant = true
    }
  } else {
    disabilityCompliantValues[field] = value
    noDisabilityCompliant = checkHasNoDisabilityCompliance(
      disabilityCompliantValues
    )
  }

  return { ...disabilityCompliantValues, noDisabilityCompliant }
}

const AccessibilityCheckboxList = ({
  onChange,
  formValues,
  isInError,
  isDisabled,
  readOnly,
}) => {
  const handleChange = useCallback(
    event => {
      onChange(
        autoFillValues(formValues, event.target.name, event.target.checked)
      )
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
        <InputError>Veuillez cocher au moins une option ci-dessus</InputError>
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
