import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import Select from 'components/layout/inputs/Select'
import { CATEGORY_STATUS } from 'core/Offers'
import { sortByDisplayName } from 'utils/strings'

import { DEFAULT_FORM_VALUES } from '../../_constants'

import { SubtypeSelects } from './SubtypeSelects'

const OfferCategories = ({
  categories,
  getErrorMessage,
  categoriesFormValues,
  isVirtualOffer,
  isTypeOfflineButOnlyVirtualVenues,
  readOnlyFields,
  resetFormError,
  subCategories,
  updateCategoriesFormValues,
  updateFormErrors,
}) => {
  const categoryIsVirtual = useCallback(
    categoryId => {
      return (
        subCategories.filter(
          s =>
            s.categoryId === categoryId &&
            [
              CATEGORY_STATUS.ONLINE,
              CATEGORY_STATUS.ONLINE_OR_OFFLINE,
            ].includes(s.onlineOfflinePlatform)
        ).length > 0
      )
    },
    [subCategories]
  )
  const categoryFilters = useCallback(
    category => {
      return (
        category.isSelectable &&
        (!isVirtualOffer || categoryIsVirtual(category.id))
      )
    },
    [categoryIsVirtual, isVirtualOffer]
  )

  const categoriesOptions = sortByDisplayName(
    categories.filter(categoryFilters).map(item => ({
      id: item['id'].toString(),
      displayName: item['proLabel'],
    }))
  )
  const [subCategoriesOptions, setSubCategoriesOptions] = useState(null)
  const [subCategoryConditionalFields, setSubCategoryConditionalFields] =
    useState([])

  useEffect(
    function onCategoryChange() {
      if (categoriesFormValues.categoryId !== DEFAULT_FORM_VALUES.categoryId) {
        let options = subCategories.filter(
          subCategory =>
            subCategory.categoryId === categoriesFormValues.categoryId &&
            subCategory.isSelectable
        )
        if (isVirtualOffer) {
          options = options.filter(option =>
            [
              CATEGORY_STATUS.ONLINE,
              CATEGORY_STATUS.ONLINE_OR_OFFLINE,
            ].includes(option.onlineOfflinePlatform)
          )
        }
        updateFormErrors({})
        setSubCategoriesOptions(
          sortByDisplayName(
            options.map(item => ({
              id: item['id'].toString(),
              displayName: item['proLabel'],
            }))
          )
        )
      } else {
        setSubCategoriesOptions(null)
      }
    },
    [
      categoriesFormValues.categoryId,
      isVirtualOffer,
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
      if (fieldValue !== null) {
        resetFormError(fieldName)
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
    [
      categoriesFormValues,
      updateCategoriesFormValues,
      getDefaultSubCategory,
      resetFormError,
    ]
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
            getErrorMessage={getErrorMessage}
            handleSelection={handleChange}
            readOnlyFields={readOnlyFields}
          />
        )}
    </>
  )
}

OfferCategories.defaultProps = {
  isTypeOfflineButOnlyVirtualVenues: false,
  isVirtualOffer: false,
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
  isVirtualOffer: PropTypes.bool,
  readOnlyFields: PropTypes.arrayOf(PropTypes.string).isRequired,
  resetFormError: PropTypes.func.isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  updateCategoriesFormValues: PropTypes.func.isRequired,
  updateFormErrors: PropTypes.func.isRequired,
}

export default OfferCategories
