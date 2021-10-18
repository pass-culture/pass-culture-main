import PropTypes from 'prop-types'
import React from 'react'

import { RadioInput } from 'components/layout/inputs/RadioInput/RadioInput'

import { OFFER_OPTIONS } from '../../_constants'

const OfferOptions = ({
  canOfferBeDuo,
  canOfferBeEducational,
  isDuo,
  isEducational,
  isDuoDisabled,
  isEducationalDisabled,
  updateForm,
}) => {
  const handleOtherRadioInputChange = event => {
    const updatedValues = {}
    if (canOfferBeEducational) {
      updatedValues['isEducational'] = event.target.value === OFFER_OPTIONS.EDUCATIONAL
    }
    if (canOfferBeDuo) {
      updatedValues['isDuo'] = event.target.value === OFFER_OPTIONS.DUO
    }
    updateForm(updatedValues)
  }

  const noOptionSelected = !(canOfferBeEducational && isEducational) && !(canOfferBeDuo && isDuo)

  const isSelectedOptionDisabled =
    (isDuo && isDuoDisabled) || (isEducational && isEducationalDisabled)

  const areAllPresentsOfferOptionsDisabled = () => {
    let areAllOfferPresentsOfferTypesDisabled = true
    if (canOfferBeEducational) {
      areAllOfferPresentsOfferTypesDisabled =
        areAllOfferPresentsOfferTypesDisabled && isEducationalDisabled
    }
    if (canOfferBeDuo) {
      areAllOfferPresentsOfferTypesDisabled = areAllOfferPresentsOfferTypesDisabled && isDuoDisabled
    }

    return areAllOfferPresentsOfferTypesDisabled
  }

  if (!canOfferBeDuo && !canOfferBeEducational) {
    return null
  }

  return (
    <section className="form-section">
      <h3 className="section-title">
        Autres caractéristiques
      </h3>

      {canOfferBeDuo && (
        <div className="form-row">
          <RadioInput
            checked={isDuo || false}
            disabled={isDuoDisabled || isSelectedOptionDisabled}
            label={'Accepter les réservations "duo"'}
            name="offerOption"
            onChange={handleOtherRadioInputChange}
            subLabel="En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l‘accompagnateur."
            value={OFFER_OPTIONS.DUO}
          />
        </div>
      )}

      {canOfferBeEducational && (
        <div className="form-row">
          <RadioInput
            checked={isEducational || false}
            disabled={isEducationalDisabled || isSelectedOptionDisabled}
            label="Offre collective EAC"
            name="offerOption"
            onChange={handleOtherRadioInputChange}
            subLabel="Réservé uniquement aux offres s’inscrivant dans le cadre d’un projet d’Éducation Artistique et Culturelle des académies de Rennes et Versailles."
            value={OFFER_OPTIONS.EDUCATIONAL}
          />
        </div>
      )}

      <div className="form-row">
        <RadioInput
          checked={noOptionSelected || false}
          disabled={areAllPresentsOfferOptionsDisabled() || isSelectedOptionDisabled}
          label="Aucune"
          name="offerOption"
          onChange={handleOtherRadioInputChange}
          value={OFFER_OPTIONS.NONE}
        />
      </div>
    </section>
  )
}

OfferOptions.propTypes = {
  canOfferBeDuo: PropTypes.bool.isRequired,
  canOfferBeEducational: PropTypes.bool.isRequired,
  isDuo: PropTypes.bool.isRequired,
  isDuoDisabled: PropTypes.bool.isRequired,
  isEducational: PropTypes.bool.isRequired,
  isEducationalDisabled: PropTypes.bool.isRequired,
  updateForm: PropTypes.func.isRequired,
}

export default OfferOptions
