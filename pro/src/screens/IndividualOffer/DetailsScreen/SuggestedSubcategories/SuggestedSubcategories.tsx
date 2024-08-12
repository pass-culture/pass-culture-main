import { useFormikContext } from 'formik'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'
import { DetailsFormValues } from '../types'
import {
  onSuggestedSubcategoriesChange,
  onSubcategoryChange,
  onCategoryChange,
  buildCategoryOptions,
  buildSubcategoryOptions,
} from '../utils'

import styles from './SuggestedSubcategories.module.scss'

type SuggestedSubcategoriesProps = {
  suggestedSubcategories: string[]
  readOnlyFields: string[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
}

export function SuggestedSubcategories({
  suggestedSubcategories,
  readOnlyFields,
  filteredCategories,
  filteredSubcategories,
}: SuggestedSubcategoriesProps) {
  const { subCategories } = useIndividualOfferContext()
  const {
    values: { categoryId, subcategoryConditionalFields, suggestedSubcategory },
    handleChange,
    setFieldValue,
  } = useFormikContext<DetailsFormValues>()

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(subCategories, categoryId)

  return (
    <FormLayout.Section title={'Type d’offre'}>
      <FormLayout.Row>
        <div className={styles['suggested-subcategories']}>
          <p className={styles['description']}>
            Catégories suggérées pour votre offre&nbsp;:
          </p>
          <div className={styles['items']}>
            {suggestedSubcategories.map((suggestedSubcategoryId) => (
              <RadioButton
                label={
                  subCategories.find(
                    (subcategory) => subcategory.id === suggestedSubcategoryId
                  )?.proLabel ?? ''
                }
                className={styles['suggested-subcategory']}
                name="suggestedSubcategory"
                value={suggestedSubcategoryId}
                key={suggestedSubcategoryId}
                withBorder
                onChange={async (event) => {
                  await onSuggestedSubcategoriesChange({
                    event,
                    setFieldValue,
                    subcategoryConditionalFields,
                    subcategories: subCategories,
                    onSubcategoryChange,
                  })
                  handleChange(event)
                }}
              />
            ))}
            <RadioButton
              label="Autre"
              name="suggestedSubcategory"
              className={styles['suggested-subcategory']}
              value="OTHER"
              withBorder
              onChange={async (event) => {
                await onSuggestedSubcategoriesChange({
                  event,
                  setFieldValue,
                  subcategoryConditionalFields,
                  subcategories: subCategories,
                  onSubcategoryChange,
                })
                handleChange(event)
              }}
            />
          </div>
        </div>
      </FormLayout.Row>
      {suggestedSubcategory === 'OTHER' && (
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
              Une sélection précise de vos catégories permettra au grand public
              de facilement trouver votre offre. Une fois validées, vous ne
              pourrez pas les modifier.
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
              })
              handleChange(event)
            }}
          />
        </FormLayout.Row>
      )}
      {categoryId !== DEFAULT_DETAILS_FORM_VALUES.categoryId &&
        suggestedSubcategory === 'OTHER' && (
          <FormLayout.Row>
            <Select
              label="Sous-catégorie"
              name="subcategoryId"
              options={subcategoryOptions}
              defaultOption={{
                label: 'Choisir une sous-catégorie',
                value: DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
              }}
              onChange={async (event: React.ChangeEvent<HTMLSelectElement>) => {
                await onSubcategoryChange({
                  newSubCategoryId: event.target.value,
                  subcategories: filteredSubcategories,
                  setFieldValue,
                  subcategoryConditionalFields,
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
    </FormLayout.Section>
  )
}
