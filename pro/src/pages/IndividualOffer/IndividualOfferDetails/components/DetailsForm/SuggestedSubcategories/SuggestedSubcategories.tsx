import { useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  SuggestedSubcategoriesResponseModel,
} from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  onSubcategoryChange,
  onCategoryChange,
  buildCategoryOptions,
  buildSubcategoryOptions,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from './SuggestedSubcategories.module.scss'

export type SuggestedSubcategoriesProps = {
  hasApiBeenCalled: boolean
  suggestedSubcategories: SuggestedSubcategoriesResponseModel['subcategoryIds']
  readOnlyFields: string[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
}

export function SuggestedSubcategories({
  hasApiBeenCalled,
  suggestedSubcategories,
  readOnlyFields,
  filteredCategories,
  filteredSubcategories,
}: SuggestedSubcategoriesProps) {
  const [prevSelectedSubCategory, setPrevSelectedFromPrevSuggestions] =
    useState<string | null>(null)
  const { subCategories, setIsEvent } = useIndividualOfferContext()
  const {
    values: {
      categoryId,
      subcategoryConditionalFields,
      suggestedSubcategory: selectedSubCategory,
    },
    handleChange,
    setFieldValue,
  } = useFormikContext<DetailsFormValues>()

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
  )

  // Suggested subcategories have changed and current selection
  // is not in this list anymore. Yet, we'd like to
  // display it as a selected radio button.
  const isSelectedFromPrevSuggestions =
    selectedSubCategory &&
    selectedSubCategory !== 'OTHER' &&
    !suggestedSubcategories.includes(selectedSubCategory)
  const wasSelectedFromPrevSuggestions = prevSelectedSubCategory !== null

  // Clean start: on suggested subcategories change,
  // only the suggested subcategories list and current selection
  // are to be displayed.
  useEffect(() => {
    setPrevSelectedFromPrevSuggestions(null)
  }, [suggestedSubcategories])

  const onRadioButtonChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ): Promise<void> => {
    const id = event.target.value
    const isSubcategoryId = id !== 'OTHER'
    const subCategory: SubcategoryResponseModel | null = isSubcategoryId
      ? subCategories.find((subcategory) => subcategory.id === id) || null
      : null

    if (isSelectedFromPrevSuggestions) {
      // If previous selection belongs to a previous list of suggested subcategories,
      // it will be stored to be displayed as an unselected radio button
      // so it doesn't disappear onSuggestedSubcategoriesChange.
      setPrevSelectedFromPrevSuggestions(selectedSubCategory)
    }

    if (subCategory) {
      await setFieldValue('categoryId', subCategory.categoryId)
      await setFieldValue('subcategoryId', id)
      await onSubcategoryChange({
        newSubCategoryId: id,
        subcategories: subCategories,
        setFieldValue,
        subcategoryConditionalFields,
        setIsEvent,
      })
    } else {
      const { categoryId, subcategoryId } = DEFAULT_DETAILS_FORM_VALUES
      await setFieldValue('categoryId', categoryId)
      await setFieldValue('subcategoryId', subcategoryId)
    }

    handleChange(event)
  }

  const renderRadioButton = (id: string) => {
    const isSubcategoryId = id !== 'OTHER'
    const label = isSubcategoryId
      ? subCategories.find((subcat) => subcat.id === id)?.proLabel || ''
      : 'Autre'

    return (
      <RadioButton
        label={label}
        className={styles['suggested-subcategory']}
        name="suggestedSubcategory"
        value={id}
        key={id}
        variant={RadioVariant.BOX}
        onChange={onRadioButtonChange}
      />
    )
  }

  return (
    <FormLayout.Section
      title={'Type d’offre'}
      className={styles['suggested-subcategories-section']}
    >
      <FormLayout.Row>
        <div className={styles['suggested-subcategories']}>
          <p
            id="suggested-subcategories-title"
            className={styles['description']}
          >
            Catégories suggérées pour votre offre :
          </p>
          <div
            className={styles['items']}
            id="suggested-subcategories"
            aria-labelledby="suggested-subcategories-title"
            role="status"
          >
            {hasApiBeenCalled ? (
              <>
                {suggestedSubcategories.map(renderRadioButton)}
                {isSelectedFromPrevSuggestions &&
                  renderRadioButton(selectedSubCategory)}
                {wasSelectedFromPrevSuggestions &&
                  prevSelectedSubCategory !== selectedSubCategory &&
                  renderRadioButton(prevSelectedSubCategory)}
                {renderRadioButton('OTHER')}
              </>
            ) : (
              <span>Veuillez renseigner un titre ou une description.</span>
            )}
          </div>
        </div>
      </FormLayout.Row>
      {selectedSubCategory === 'OTHER' && (
        <>
          <FormLayout.Row
            sideComponent={
              <InfoBox
                link={{
                  isExternal: true,
                  to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
                  text: 'Quelles catégories choisir ?',
                  opensInNewTab: true,
                }}
              >
                Une sélection précise de vos catégories permettra au grand
                public de facilement trouver votre offre. Une fois validées,
                vous ne pourrez pas les modifier.
              </InfoBox>
            }
          >
            <Select
              label="Catégorie"
              name="categoryId"
              options={categoryOptions}
              defaultOption={{
                label: 'Choisir une catégorie',
                value: DEFAULT_DETAILS_FORM_VALUES.categoryId,
              }}
              disabled={readOnlyFields.includes('categoryId')}
              onChange={async (event: React.ChangeEvent<HTMLSelectElement>) => {
                await onCategoryChange({
                  categoryId: event.target.value,
                  readOnlyFields,
                  subcategories: filteredSubcategories,
                  setFieldValue,
                  onSubcategoryChange,
                  subcategoryConditionalFields,
                  setIsEvent,
                })
                handleChange(event)
              }}
            />
          </FormLayout.Row>
          {categoryId !== DEFAULT_DETAILS_FORM_VALUES.categoryId && (
            <FormLayout.Row>
              <Select
                label="Sous-catégorie"
                name="subcategoryId"
                options={subcategoryOptions}
                defaultOption={{
                  label: 'Choisir une sous-catégorie',
                  value: DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
                }}
                onChange={async (
                  event: React.ChangeEvent<HTMLSelectElement>
                ) => {
                  await onSubcategoryChange({
                    newSubCategoryId: event.target.value,
                    subcategories: filteredSubcategories,
                    setFieldValue,
                    subcategoryConditionalFields,
                    setIsEvent,
                  })
                  handleChange(event)
                }}
                disabled={
                  readOnlyFields.includes('subcategoryId') ||
                  subcategoryOptions.length === 1
                }
              />
            </FormLayout.Row>
          )}
        </>
      )}
    </FormLayout.Section>
  )
}
