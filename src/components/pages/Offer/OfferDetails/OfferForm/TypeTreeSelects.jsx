import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'

import { musicOptionsTree, showOptionsTree } from '../enums'

import { DEFAULT_FORM_VALUES } from './OfferForm'

const TypeTreeSelects = props => {
  const { isReadOnly, types, typeValues, updateTypeValues } = props

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
            displayName: 'Choisir une catégorie',
            id: DEFAULT_FORM_VALUES.type,
          }}
          handleSelection={handleChange}
          isDisabled={isReadOnly}
          label="Type"
          name="type"
          options={typeOptions}
          required
          selectedValue={typeValues.type}
        />
      </div>

      {!!subTypeOptions['musicType'].length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un genre musical',
              id: DEFAULT_FORM_VALUES.musicType,
            }}
            handleSelection={handleChange}
            isDisabled={isReadOnly}
            label="Genre musical"
            name="musicType"
            options={subTypeOptions['musicType']}
            required
            selectedValue={typeValues.musicType}
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
            handleSelection={handleChange}
            isDisabled={isReadOnly}
            label="Sous genre"
            name="musicSubType"
            options={subTypeOptions['musicSubType']}
            required
            selectedValue={typeValues.musicSubType}
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
            handleSelection={handleChange}
            isDisabled={isReadOnly}
            label="Type de spectacle"
            name="showType"
            options={subTypeOptions['showType']}
            required
            selectedValue={typeValues.showType}
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
            handleSelection={handleChange}
            isDisabled={isReadOnly}
            label="Sous type"
            name="showSubType"
            options={subTypeOptions['showSubType']}
            required
            selectedValue={typeValues.showSubType}
            sublabel="Optionnel"
          />
        </div>
      )}
    </Fragment>
  )
}

export default TypeTreeSelects
