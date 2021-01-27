import * as PropTypes from 'prop-types'
import React from 'react'

import Select from 'components/layout/inputs/Select'
import { DEFAULT_FORM_VALUES } from 'components/pages/Offer/Offer/OfferDetails/OfferForm/_constants'

export const SubtypeSelects = props => {
  const { areSubtypesVisible, disabled, handleSelection, subTypeOptions, typeValues } = props

  return areSubtypesVisible ? (
    <>
      {!!subTypeOptions['musicType'].length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un genre musical',
              id: DEFAULT_FORM_VALUES.musicType,
            }}
            handleSelection={handleSelection}
            isDisabled={disabled}
            label="Genre musical"
            name="musicType"
            options={subTypeOptions['musicType']}
            required
            selectedValue={typeValues.musicType || DEFAULT_FORM_VALUES.musicType}
            sublabel="Optionnel"
          />
        </div>
      )}

      {!!subTypeOptions['musicSubType'].length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un sous-genre',
              id: DEFAULT_FORM_VALUES.musicSubType,
            }}
            handleSelection={handleSelection}
            isDisabled={disabled}
            label="Sous genre"
            name="musicSubType"
            options={subTypeOptions['musicSubType']}
            required
            selectedValue={typeValues.musicSubType || DEFAULT_FORM_VALUES.musicSubType}
            sublabel="Optionnel"
          />
        </div>
      )}

      {!!subTypeOptions['showType'].length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un type de spectacle',
              id: DEFAULT_FORM_VALUES.showType,
            }}
            handleSelection={handleSelection}
            isDisabled={disabled}
            label="Type de spectacle"
            name="showType"
            options={subTypeOptions['showType']}
            required
            selectedValue={typeValues.showType || DEFAULT_FORM_VALUES.showType}
            sublabel="Optionnel"
          />
        </div>
      )}

      {!!subTypeOptions['showSubType'].length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un sous type',
              id: DEFAULT_FORM_VALUES.showSubType,
            }}
            handleSelection={handleSelection}
            isDisabled={disabled}
            label="Sous type"
            name="showSubType"
            options={subTypeOptions['showSubType']}
            required
            selectedValue={typeValues.showSubType || DEFAULT_FORM_VALUES.showSubType}
            sublabel="Optionnel"
          />
        </div>
      )}
    </>
  ) : null
}

SubtypeSelects.defaultProps = {
  areSubtypesVisible: true,
}

SubtypeSelects.propTypes = {
  areSubtypesVisible: PropTypes.bool,
  disabled: PropTypes.bool.isRequired,
  handleSelection: PropTypes.func.isRequired,
  subTypeOptions: PropTypes.shape({
    musicSubType: PropTypes.arrayOf(PropTypes.object),
    showType: PropTypes.arrayOf(PropTypes.object),
    musicType: PropTypes.arrayOf(PropTypes.object),
    showSubType: PropTypes.arrayOf(PropTypes.object),
  }).isRequired,
  typeValues: PropTypes.shape({
    type: PropTypes.string,
    musicType: PropTypes.string,
    musicSubType: PropTypes.string,
    showType: PropTypes.string,
    showSubType: PropTypes.string,
  }).isRequired,
}
