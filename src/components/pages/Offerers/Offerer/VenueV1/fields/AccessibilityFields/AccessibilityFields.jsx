import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as AudioDisabilitySvg } from 'icons/audio-disability.svg'
import { ReactComponent as MentalDisabilitySvg } from 'icons/mental-disability.svg'
import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'
import { ReactComponent as VisualDisabilitySvg } from 'icons/visual-disability.svg'
import { CheckboxField, Divider } from 'ui-kit'

const checkNoDisabilityCompliant = (_value, allValues) => {
  const hasAccessibility = [
    allValues.audioDisabilityCompliant,
    allValues.mentalDisabilityCompliant,
    allValues.motorDisabilityCompliant,
    allValues.visualDisabilityCompliant,
  ].includes(true)
  if (!hasAccessibility) {
    return true
  }
  return false
}

const initializeEmptyValue = fieldName => (_value, allValues) => {
  return allValues[fieldName] === undefined ? false : allValues[fieldName]
}

const setNoDisabilityCompliance = fieldName => (value, allValues) => {
  if (value) return false
  return allValues[fieldName]
}

export const autoFillNoDisabilityCompliantDecorator = createDecorator(
  {
    field: 'noDisabilityCompliant',
    updates: {
      noDisabilityCompliant: checkNoDisabilityCompliant,
      audioDisabilityCompliant: setNoDisabilityCompliance('audioDisabilityCompliant'),
      mentalDisabilityCompliant: setNoDisabilityCompliance('mentalDisabilityCompliant'),
      motorDisabilityCompliant: setNoDisabilityCompliance('motorDisabilityCompliant'),
      visualDisabilityCompliant: setNoDisabilityCompliance('visualDisabilityCompliant'),
    },
  },
  {
    field: /(audio|mental|motor|visual)DisabilityCompliant/,
    updates: {
      noDisabilityCompliant: checkNoDisabilityCompliant,
      audioDisabilityCompliant: initializeEmptyValue('audioDisabilityCompliant'),
      mentalDisabilityCompliant: initializeEmptyValue('mentalDisabilityCompliant'),
      motorDisabilityCompliant: initializeEmptyValue('motorDisabilityCompliant'),
      visualDisabilityCompliant: initializeEmptyValue('visualDisabilityCompliant'),
    },
  }
)

const AccessibilityFields = ({ formValues, readOnly, venue }) => {
  const accessibilityFieldNames = [
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
  ]
  const haveChange =
    accessibilityFieldNames.find(field => {
      return formValues && formValues[field] != venue[field]
    }) !== undefined

  return (
    <div className="section bank-information vp-content-section">
      <div className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">
          Accessibilités
        </h2>
      </div>
      <p className="bi-subtitle">
        Les modalités d’accessibilité s’appliqueront par défaut à la création de vos offres. Vous
        pourrez modifier cette information à l’échelle de l’offre.
      </p>

      <p className="bi-subtitle">
        Ce lieu est accessible aux publics en situation de handicaps :
        <span className="field-asterisk">
          *
        </span>
      </p>
      <div>
        <CheckboxField
          SvgElement={VisualDisabilitySvg}
          className="field field-checkbox"
          disabled={readOnly}
          id="visualDisabilityCompliant"
          label="Visuel"
          name="visualDisabilityCompliant"
          required
        />
        <CheckboxField
          SvgElement={MentalDisabilitySvg}
          className="field field-checkbox"
          disabled={readOnly}
          id="mentalDisabilityCompliant"
          label="Psychique ou cognitif"
          name="mentalDisabilityCompliant"
          required
        />
        <CheckboxField
          SvgElement={MotorDisabilitySvg}
          className="field field-checkbox"
          disabled={readOnly}
          id="motorDisabilityCompliant"
          label="Moteur"
          name="motorDisabilityCompliant"
          required
        />
        <CheckboxField
          SvgElement={AudioDisabilitySvg}
          className="field field-checkbox"
          disabled={readOnly}
          id="audioDisabilityCompliant"
          label="Auditif"
          name="audioDisabilityCompliant"
          required
        />
        <CheckboxField
          className="field field-checkbox"
          disabled={readOnly}
          id="noDisabilityCompliant"
          label="Non accessible"
          name="noDisabilityCompliant"
        />
      </div>
      {haveChange && (
        <>
          <Divider size="medium" />

          <CheckboxField
            className="field field-checkbox"
            disabled={readOnly}
            id="isAccessibilityAppliedOnAllOffers"
            label="Appliquer le changement à toutes les offres existantes"
            name="isAccessibilityAppliedOnAllOffers"
          />
        </>
      )}
    </div>
  )
}

AccessibilityFields.defaultProps = {
  readOnly: false,
}

AccessibilityFields.propTypes = {
  formValues: PropTypes.shape().isRequired,
  readOnly: PropTypes.bool,
  venue: PropTypes.shape().isRequired,
}

export default AccessibilityFields
