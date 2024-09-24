import { useFormikContext } from 'formik'
import { useTranslation } from 'react-i18next'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Select } from 'ui-kit/form/Select/Select'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'
import { DetailsFormValues } from '../types'
import {
  onSubcategoryChange,
  onCategoryChange,
  buildCategoryOptions,
  buildSubcategoryOptions,
} from '../utils'

import styles from './Subcategories.module.scss'

type SuggestedSubcategoriesProps = {
  readOnlyFields: string[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
}

export function Subcategories({
  readOnlyFields,
  filteredCategories,
  filteredSubcategories,
}: SuggestedSubcategoriesProps) {
  const { t } = useTranslation('common')
  const {
    values: { categoryId, subcategoryConditionalFields },
    handleChange,
    setFieldValue,
  } = useFormikContext<DetailsFormValues>()

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
  )

  return (
    <FormLayout.Section
      title={t('offer_type')}
      className={styles['subcategories-section']}
    >
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
            {t('category_selection_info')}
          </InfoBox>
        }
      >
        <Select
          label={t('category')}
          name="categoryId"
          options={categoryOptions}
          defaultOption={{
            label: t('choose_category'),
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
