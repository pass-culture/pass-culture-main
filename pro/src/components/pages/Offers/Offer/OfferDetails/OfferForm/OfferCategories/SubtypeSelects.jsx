import * as PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Select from 'components/layout/inputs/Select'

import { DEFAULT_FORM_VALUES } from '../../_constants'

import { musicOptionsTree, showOptionsTree } from './subTypes'

const initialSubTypesOptions = {
  musicType: musicOptionsTree
    .map(item => ({
      id: item['code'].toString(),
      displayName: item['label'],
    }))
    .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr')),
  showType: showOptionsTree
    .map(item => ({
      id: item['code'].toString(),
      displayName: item['label'],
    }))
    .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr')),
  musicSubType: [],
  showSubType: [],
}

export const SubtypeSelects = ({
  readOnlyFields,
  handleSelection,
  categoriesFormValues,
  currentSubCategoryConditionalFields,
  getErrorMessage,
}) => {
  const [subTypesOptions, setSubTypesOptions] = useState(initialSubTypesOptions)

  useEffect(() => {
    if (categoriesFormValues.musicType !== DEFAULT_FORM_VALUES.musicType) {
      const selectedMusicTypeChildren = musicOptionsTree.find(
        musicType => musicType.code === parseInt(categoriesFormValues.musicType)
      ).children

      setSubTypesOptions(prevOptions => ({
        ...prevOptions,
        musicSubType: selectedMusicTypeChildren
          .map(item => ({
            id: item['code'].toString(),
            displayName: item['label'],
          }))
          .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr')),
      }))
    } else {
      setSubTypesOptions(prevOptions => ({
        ...prevOptions,
        musicSubType: initialSubTypesOptions.musicSubType,
      }))
    }
  }, [categoriesFormValues.musicType])

  useEffect(() => {
    if (categoriesFormValues.showType !== DEFAULT_FORM_VALUES.showType) {
      const selectedShowTypeChildren = showOptionsTree.find(
        showType => showType.code === parseInt(categoriesFormValues.showType)
      ).children

      setSubTypesOptions(prevOptions => ({
        ...prevOptions,
        showSubType: selectedShowTypeChildren
          .map(item => ({
            id: item['code'].toString(),
            displayName: item['label'],
          }))
          .sort((a, b) => a.displayName.localeCompare(b.displayName, 'fr')),
      }))
    } else {
      setSubTypesOptions(prevOptions => ({
        ...prevOptions,
        showSubType: initialSubTypesOptions.showSubType,
      }))
    }
  }, [categoriesFormValues.showType])

  return (
    <>
      {currentSubCategoryConditionalFields.includes('musicType') && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un genre musical',
              id: DEFAULT_FORM_VALUES.musicType,
            }}
            error={getErrorMessage('musicType')}
            handleSelection={handleSelection}
            isDisabled={readOnlyFields.includes('musicType')}
            label="Genre musical"
            name="musicType"
            options={subTypesOptions.musicType}
            required
            selectedValue={
              categoriesFormValues.musicType || DEFAULT_FORM_VALUES.musicType
            }
          />
        </div>
      )}

      {!!subTypesOptions?.musicSubType.length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un sous-genre',
              id: DEFAULT_FORM_VALUES.musicSubType,
            }}
            error={getErrorMessage('musicSubType')}
            handleSelection={handleSelection}
            isDisabled={readOnlyFields.includes('musicSubType')}
            label="Sous genre"
            name="musicSubType"
            options={subTypesOptions.musicSubType}
            required
            selectedValue={
              categoriesFormValues.musicSubType ||
              DEFAULT_FORM_VALUES.musicSubType
            }
          />
        </div>
      )}

      {currentSubCategoryConditionalFields.includes('showType') && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un type de spectacle',
              id: DEFAULT_FORM_VALUES.showType,
            }}
            error={getErrorMessage('showType')}
            handleSelection={handleSelection}
            isDisabled={readOnlyFields.includes('showType')}
            label="Type de spectacle"
            name="showType"
            options={subTypesOptions.showType}
            required
            selectedValue={
              categoriesFormValues.showType || DEFAULT_FORM_VALUES.showType
            }
          />
        </div>
      )}

      {!!subTypesOptions?.showSubType.length && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: 'Choisir un sous type',
              id: DEFAULT_FORM_VALUES.showSubType,
            }}
            error={getErrorMessage('showSubType')}
            handleSelection={handleSelection}
            isDisabled={readOnlyFields.includes('showSubType')}
            label="Sous type"
            name="showSubType"
            options={subTypesOptions.showSubType}
            required
            selectedValue={
              categoriesFormValues.showSubType ||
              DEFAULT_FORM_VALUES.showSubType
            }
          />
        </div>
      )}
    </>
  )
}

SubtypeSelects.propTypes = {
  categoriesFormValues: PropTypes.shape({
    musicType: PropTypes.string,
    musicSubType: PropTypes.string,
    showType: PropTypes.string,
    showSubType: PropTypes.string,
  }).isRequired,
  currentSubCategoryConditionalFields: PropTypes.arrayOf(PropTypes.string)
    .isRequired,
  getErrorMessage: PropTypes.string.isRequired,
  handleSelection: PropTypes.func.isRequired,
  readOnlyFields: PropTypes.arrayOf(PropTypes.string).isRequired,
}
