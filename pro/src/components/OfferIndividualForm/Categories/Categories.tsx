import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import BannerAddVenue from 'components/Banner/BannerAddVenue'
import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import { InfoBox, Select } from 'ui-kit'

import styles from '../OfferIndividualForm.module.scss'
import { onVenueChange } from '../UsefulInformations/Venue/Venue'
import buildSubCategoryFields from '../utils/buildSubCategoryFields'
import { getFilteredVenueList } from '../utils/getFilteredVenueList'

import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from './constants'
import { MusicTypes } from './MusicTypes'
import { OfferSubtypeTag } from './OfferSubtypeTag/OfferSubtypeTag'
import { ShowTypes } from './ShowTypes'

export interface ICategoriesProps {
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  readOnlyFields?: string[]
  showAddVenueBanner?: boolean
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
  venueList: TOfferIndividualVenue[]
}

const buildCategoryOptions = (categories: IOfferCategory[]): SelectOption[] =>
  categories
    .map((category: IOfferCategory) => ({
      value: category.id,
      label: category.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

const buildSubcategoryOptions = (
  subCategories: IOfferSubCategory[],
  categoryId: string
): SelectOption[] =>
  buildCategoryOptions(
    subCategories.filter(
      (subCategory: IOfferSubCategory) => subCategory.categoryId === categoryId
    )
  )

const Categories = ({
  categories,
  subCategories,
  readOnlyFields = [],
  showAddVenueBanner = false,
  offerSubtype,
  venueList,
}: ICategoriesProps): JSX.Element => {
  const {
    values: { categoryId, subCategoryFields, offererId },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()
  const categoryOptions = buildCategoryOptions(categories)
  const subcategoryOptions = buildSubcategoryOptions(subCategories, categoryId)

  const onSubCategoryChange = (newSubCategory: string) => {
    const { subCategoryFields: newSubCategoryFields, isEvent } =
      buildSubCategoryFields(newSubCategory, subCategories)
    setFieldValue('subCategoryFields', newSubCategoryFields)
    setFieldValue('isEvent', isEvent)
    setFieldValue(
      'isDuo',
      Boolean(subCategories.find(s => s.id == newSubCategory)?.canBeDuo)
    )
    if (newSubCategoryFields === subCategoryFields) {
      return
    }

    const fieldsToReset = subCategoryFields.filter(
      (field: string) => !newSubCategoryFields.includes(field)
    )
    fieldsToReset.forEach((field: string) => {
      if (field in SUBCATEGORIES_FIELDS_DEFAULT_VALUES) {
        setFieldValue(
          field,
          SUBCATEGORIES_FIELDS_DEFAULT_VALUES[
            field as keyof typeof SUBCATEGORIES_FIELDS_DEFAULT_VALUES
          ]
        )
      }
    })

    const venues = getFilteredVenueList(
      newSubCategory,
      subCategories,
      venueList
    )
    if (venues.length === 1) {
      setFieldValue('venueId', venues[0].nonHumanizedId)
      onVenueChange(
        setFieldValue,
        venueList,
        venues[0].nonHumanizedId.toString()
      )
    }
  }

  const onCategoryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    if (readOnlyFields.includes('subcategoryId')) {
      return
    }
    const newSubcategoryOptions = buildSubcategoryOptions(
      subCategories,
      event.target.value
    )
    const subCategoryId =
      newSubcategoryOptions.length === 1
        ? String(newSubcategoryOptions[0].value)
        : FORM_DEFAULT_VALUES.subcategoryId
    setFieldValue('subcategoryId', subCategoryId, false)
    onSubCategoryChange(subCategoryId)
  }

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
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
              text: 'Quelles catégories choisir ?',
              target: '_blank',
              rel: 'noopener noreferrer',
            }}
          >
            Une sélection précise de vos catégories permettra au grand public de
            facilement trouver votre offre. Une fois validées, vous ne pourrez
            pas les modifier.
          </InfoBox>
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
          onChange={onCategoryChange}
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
            onChange={(event: React.ChangeEvent<HTMLSelectElement>) =>
              onSubCategoryChange(event.target.value)
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
