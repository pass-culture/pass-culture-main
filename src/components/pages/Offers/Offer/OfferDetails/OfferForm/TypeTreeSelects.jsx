import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import { SubtypeSelects } from 'components/pages/Offers/Offer/OfferDetails/OfferForm/SubtypeSelects'

import { musicOptionsTree, showOptionsTree } from '../subTypes'

import { DEFAULT_FORM_VALUES } from './_constants'

const TypeTreeSelects = props => {
  const { areSubtypesVisible, isReadOnly, types, typeValues, updateTypeValues } = props

  const typeOptions = buildSelectOptions('value', 'proLabel', types)
  const [subTypeOptions, setSubTypeOptions] = useState({
    musicType: [],
    musicSubType: [],
    showType: [],
    showSubType: [],
  })

  const hasConditionalField = useCallback(
    (typeValue, fieldName) => {
      if (!typeValue || !typeValue.length) {
        return false
      }

      const selectedType = types.find(type => type.value === typeValue)
      if (!selectedType) return false

      return selectedType.conditionalFields.includes(fieldName)
    },
    [types]
  )

  const buildTreeSelectOptions = useCallback(
    fieldName => {
      if (
        isReadOnly &&
        (!typeValues[fieldName] || typeValues[fieldName] === DEFAULT_FORM_VALUES[fieldName])
      ) {
        return []
      }

      if (fieldName === 'type') {
        return buildSelectOptions('value', 'proLabel', types)
      }

      if (typeValues.type !== DEFAULT_FORM_VALUES.type) {
        switch (fieldName) {
          case 'musicType': {
            if (hasConditionalField(typeValues.type, 'musicType')) {
              return buildSelectOptions('code', 'label', musicOptionsTree)
            }
            break
          }
          case 'showType': {
            if (hasConditionalField(typeValues.type, 'showType')) {
              return buildSelectOptions('code', 'label', showOptionsTree)
            }
            break
          }
          case 'musicSubType': {
            if (
              typeValues.musicType !== DEFAULT_FORM_VALUES.musicType &&
              hasConditionalField(typeValues.type, 'musicType')
            ) {
              const musicType = musicOptionsTree.find(
                musicType => musicType.code === parseInt(typeValues.musicType)
              )
              return buildSelectOptions('code', 'label', musicType.children)
            }
            break
          }
          case 'showSubType': {
            if (
              typeValues.showType !== DEFAULT_FORM_VALUES.musicType &&
              hasConditionalField(typeValues.type, 'showType')
            ) {
              const showType = showOptionsTree.find(
                showType => showType.code === parseInt(typeValues.showType)
              )
              return buildSelectOptions('code', 'label', showType.children)
            }
            break
          }
        }
      }

      return []
    },
    [hasConditionalField, isReadOnly, types, typeValues]
  )

  useEffect(() => {
    setSubTypeOptions({
      musicType: buildTreeSelectOptions('musicType'),
      musicSubType: buildTreeSelectOptions('musicSubType'),
      showType: buildTreeSelectOptions('showType'),
      showSubType: buildTreeSelectOptions('showSubType'),
    })
  }, [buildTreeSelectOptions])

  const handleChange = useCallback(
    event => {
      const fieldName = event.target.name
      const fieldValue = event.target.value
      const newTypeValues = {
        ...typeValues,
        [fieldName]: fieldValue,
      }

      if (typeValues[fieldName] === newTypeValues[fieldName]) {
        return
      }

      const resetFieldsByChangedField = {
        type: ['musicType', 'musicSubType', 'showType', 'showSubType'],
        musicType: ['musicSubType', 'showType', 'showSubType'],
        musicSubType: [],
        showType: ['musicType', 'musicSubType', 'showSubType'],
        showSubType: [],
      }
      resetFieldsByChangedField[fieldName].forEach(fieldName => {
        newTypeValues[fieldName] = DEFAULT_FORM_VALUES[fieldName]
      })

      updateTypeValues(newTypeValues)
    },
    [updateTypeValues, typeValues]
  )

  return (
    <Fragment>
      <div className="form-row">
        <Select
          defaultOption={{
            displayName: 'Choisir un type',
            id: DEFAULT_FORM_VALUES.type,
          }}
          handleSelection={handleChange}
          isDisabled={isReadOnly}
          label="Type"
          name="type"
          options={typeOptions}
          required
          selectedValue={typeValues.type || DEFAULT_FORM_VALUES.type}
        />
      </div>
      <SubtypeSelects
        areSubtypesVisible={areSubtypesVisible}
        disabled={isReadOnly}
        handleSelection={handleChange}
        subTypeOptions={subTypeOptions}
        typeValues={typeValues}
      />
    </Fragment>
  )
}

TypeTreeSelects.defaultProps = {
  areSubtypesVisible: true,
}

TypeTreeSelects.propTypes = {
  areSubtypesVisible: PropTypes.bool,
  isReadOnly: PropTypes.bool.isRequired,
  typeValues: PropTypes.shape({
    musicSubType: PropTypes.string,
    musicType: PropTypes.string,
    showSubType: PropTypes.string,
    showType: PropTypes.string,
    type: PropTypes.string,
  }).isRequired,
  types: PropTypes.arrayOf().isRequired,
  updateTypeValues: PropTypes.func.isRequired,
}

export default TypeTreeSelects
