import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import Select, { buildSelectOptions } from 'components/layout/inputs/Select'

import { DEFAULT_FORM_VALUES } from '../../_constants'

import { SubtypeSelects } from './SubtypeSelects'

const OfferCategories = ({
  categories,
  getErrorMessage,
  categoriesFormValues,
  isTypeOfflineButOnlyVirtualVenues,
  readOnlyFields,
  subCategories,
  updateCategoriesFormValues,
  updateFormErrors,
}) => {
  const categoriesOptions = buildSelectOptions(
    'id',
    'proLabel',
    categories.filter(category => category.isSelectable)
  )
  const [subCategoriesOptions, setSubCategoriesOptions] = useState(null)
  const [subCategoryConditionalFields, setSubCategoryConditionalFields] =
    useState([])

  useEffect(
    function onCategoryChange() {
      if (categoriesFormValues.categoryId !== DEFAULT_FORM_VALUES.categoryId) {
        const options = subCategories.filter(
          subCategory =>
            subCategory.categoryId === categoriesFormValues.categoryId &&
            subCategory.isSelectable
        )
        updateFormErrors({})
        setSubCategoriesOptions(buildSelectOptions('id', 'proLabel', options))
      } else {
        setSubCategoriesOptions(null)
      }
    },
    [
      categoriesFormValues.categoryId,
      subCategories,
      updateCategoriesFormValues,
      updateFormErrors,
    ]
  )

  useEffect(
    function onSubCategoryChange() {
      if (
        categoriesFormValues.subcategoryId !== DEFAULT_FORM_VALUES.subcategoryId
      ) {
        const currentSubCategoryConditionalFields = subCategories
          .find(
            subCategory => categoriesFormValues.subcategoryId === subCategory.id
          )
          .conditionalFields.filter(
            field => field === 'musicType' || field === 'showType'
          )
        updateFormErrors({})
        setSubCategoryConditionalFields(currentSubCategoryConditionalFields)
      } else {
        setSubCategoryConditionalFields([])
      }
    },
    [categoriesFormValues.subcategoryId, subCategories, updateFormErrors]
  )

  const getDefaultSubCategory = useCallback(
    categoryId => {
      const categorySubCategories = subCategories.filter(
        subCategory =>
          subCategory.categoryId === categoryId && subCategory.isSelectable
      )
      return categorySubCategories.length === 1
        ? categorySubCategories[0].id
        : DEFAULT_FORM_VALUES.categoryId
    },
    [subCategories]
  )

  const handleChange = useCallback(
    event => {
      const fieldName = event.target.name
      const fieldValue = event.target.value

      if (categoriesFormValues[fieldName] === fieldValue) {
        return
      }

      let newCategoriesFormValues = {}

      switch (fieldName) {
        case 'categoryId':
          newCategoriesFormValues = {
            categoryId: fieldValue,
            subcategoryId: getDefaultSubCategory(fieldValue),
            musicType: DEFAULT_FORM_VALUES.musicType,
            musicSubType: DEFAULT_FORM_VALUES.musicSubType,
            showType: DEFAULT_FORM_VALUES.showType,
            showSubType: DEFAULT_FORM_VALUES.showSubType,
          }
          break
        case 'subcategoryId':
          newCategoriesFormValues = {
            ...categoriesFormValues,
            subcategoryId: fieldValue,
            musicType: DEFAULT_FORM_VALUES.musicType,
            musicSubType: DEFAULT_FORM_VALUES.musicSubType,
            showType: DEFAULT_FORM_VALUES.showType,
            showSubType: DEFAULT_FORM_VALUES.showSubType,
          }
          break
        case 'musicType':
          newCategoriesFormValues = {
            ...categoriesFormValues,
            musicType: fieldValue,
            musicSubType: DEFAULT_FORM_VALUES.musicSubType,
            showType: DEFAULT_FORM_VALUES.showType,
            showSubType: DEFAULT_FORM_VALUES.showSubType,
          }
          break
        case 'showType':
          newCategoriesFormValues = {
            ...categoriesFormValues,
            musicType: DEFAULT_FORM_VALUES.musicType,
            musicSubType: DEFAULT_FORM_VALUES.musicSubType,
            showType: fieldValue,
            showSubType: DEFAULT_FORM_VALUES.showSubType,
          }
          break
        default:
          newCategoriesFormValues = {
            ...categoriesFormValues,
            [fieldName]: fieldValue,
          }
      }

      updateCategoriesFormValues(newCategoriesFormValues)
    },
    [categoriesFormValues, updateCategoriesFormValues, getDefaultSubCategory]
  )

  return (
    <>
      <div className="form-row">
        <Select
          defaultOption={{
            displayName: `Choisir une catégorie`,
            id: DEFAULT_FORM_VALUES.categoryId,
          }}
          error={getErrorMessage('categoryId')}
          handleSelection={handleChange}
          isDisabled={readOnlyFields.includes('categoryId')}
          label="Catégorie"
          name="categoryId"
          options={categoriesOptions}
          required
          selectedValue={
            categoriesFormValues.categoryId || DEFAULT_FORM_VALUES.categoryId
          }
        />
      </div>

      {subCategoriesOptions && (
        <div className="form-row">
          <Select
            defaultOption={{
              displayName: `Choisir une sous-catégorie`,
              id: DEFAULT_FORM_VALUES.subcategoryId,
            }}
            error={getErrorMessage('subcategoryId')}
            handleSelection={handleChange}
            isDisabled={readOnlyFields.includes('subcategoryId')}
            label="Sous-catégorie"
            name="subcategoryId"
            options={subCategoriesOptions}
            required
            selectedValue={
              categoriesFormValues.subcategoryId ||
              DEFAULT_FORM_VALUES.subcategoryId
            }
          />
        </div>
      )}

      {!isTypeOfflineButOnlyVirtualVenues &&
        subCategoryConditionalFields.length > 0 && (
          <SubtypeSelects
            categoriesFormValues={categoriesFormValues}
            currentSubCategoryConditionalFields={subCategoryConditionalFields}
            handleSelection={handleChange}
            readOnlyFields={readOnlyFields}
          />
        )}
    </>
  )
}

OfferCategories.defaultProps = {
  isTypeOfflineButOnlyVirtualVenues: false,
}

OfferCategories.propTypes = {
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  categoriesFormValues: PropTypes.shape({
    musicSubType: PropTypes.string,
    musicType: PropTypes.string,
    showSubType: PropTypes.string,
    showType: PropTypes.string,
    categoryId: PropTypes.string,
    subcategoryId: PropTypes.string,
  }).isRequired,
  getErrorMessage: PropTypes.func.isRequired,
  isTypeOfflineButOnlyVirtualVenues: PropTypes.bool,
  readOnlyFields: PropTypes.arrayOf(PropTypes.string).isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  updateCategoriesFormValues: PropTypes.func.isRequired,
  updateFormErrors: PropTypes.func.isRequired,
}

export default OfferCategories
