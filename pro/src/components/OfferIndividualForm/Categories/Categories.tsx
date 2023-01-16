import cn from 'classnames'
import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import BannerAddVenue from 'components/Banner/BannerAddVenue'
import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { InfoBox, Select } from 'ui-kit'

import styles from '../OfferIndividualForm.module.scss'

import { useSubcategoryOptions } from './hooks/useSubcategoryOptions'
import useSubCategoryUpdates from './hooks/useSubCategoryUpdates/useSubCategoryUpdates'
import { MusicTypes } from './MusicTypes'
import { OfferSubtypeTag } from './OfferSubtypeTag/OfferSubtypeTag'
import { ShowTypes } from './ShowTypes'

export interface ICategoriesProps {
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  readOnlyFields?: string[]
  showAddVenueBanner?: boolean
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
}

const buildCategoryOptions = (categories: IOfferCategory[]) => {
  return categories
    .map((c: IOfferCategory) => ({
      value: c.id,
      label: c.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

const Categories = ({
  categories,
  subCategories,
  readOnlyFields = [],
  showAddVenueBanner = false,
  offerSubtype,
}: ICategoriesProps): JSX.Element => {
  const {
    values: { categoryId, subCategoryFields, offererId },
    setFieldValue,
    setTouched,
    touched,
  } = useFormikContext<IOfferIndividualFormValues>()
  const subcategoryOptions = useSubcategoryOptions(subCategories, categoryId)
  const [categoryOptions, setCategoryOptions] = useState<SelectOptions>(
    buildCategoryOptions(categories)
  )
  useEffect(() => {
    setCategoryOptions(buildCategoryOptions(categories))
  }, [categories])

  useEffect(() => {
    if (touched.categoryId && !readOnlyFields.includes('subcategoryId')) {
      /* istanbul ignore next: DEBT, TO FIX */
      if (subcategoryOptions.length === 1) {
        setFieldValue('subcategoryId', subcategoryOptions[0].value, false)
      } else {
        setFieldValue('subcategoryId', FORM_DEFAULT_VALUES.subcategoryId, false)
        setTouched({ categoryId: true })
      }
    }
  }, [subcategoryOptions])

  useSubCategoryUpdates({ subCategories })

  const hasSubCategory = categoryId !== FORM_DEFAULT_VALUES.categoryId
  const hasMusicType = subCategoryFields.includes('musicType')
  const hasShowType = subCategoryFields.includes('showType')

  return (
    <FormLayout.Section
      title={
        <>
          <span>Type d’offre</span>
          {offerSubtype !== null && (
            <OfferSubtypeTag
              className={styles['offer-type-tag']}
              offerSubtype={offerSubtype}
            />
          )}
        </>
      }
    >
      <FormLayout.Row
        className={cn({
          [styles['category-row']]: !(hasSubCategory || showAddVenueBanner),
        })}
        sideComponent={
          <InfoBox
            type="info"
            text="Une sélection précise de vos catégories permettra au grand public de facilement trouver votre offre. Une fois validées, vous ne pourrez pas les modifier."
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
              text: 'Quelles catégories choisir ?',
              target: '_blank',
              rel: 'noopener noreferrer',
            }}
          />
        }
      >
        <Select
          label="Catégorie"
          name="categoryId"
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: FORM_DEFAULT_VALUES.categoryId,
          }}
          disabled={readOnlyFields.includes('categoryId')}
        />
      </FormLayout.Row>

      {hasSubCategory && (
        <FormLayout.Row>
          <Select
            label="Sous-catégorie"
            name="subcategoryId"
            options={subcategoryOptions}
            defaultOption={{
              label: 'Choisir une sous-catégorie',
              value: FORM_DEFAULT_VALUES.subcategoryId,
            }}
            disabled={
              readOnlyFields.includes('subcategoryId') ||
              subcategoryOptions.length === 1
            }
          />
        </FormLayout.Row>
      )}

      {hasMusicType && (
        <MusicTypes readOnly={readOnlyFields.includes('musicType')} />
      )}

      {hasShowType && (
        <ShowTypes readOnly={readOnlyFields.includes('showType')} />
      )}
      {showAddVenueBanner && (
        <FormLayout.Row>
          <BannerAddVenue offererId={offererId} />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Categories
