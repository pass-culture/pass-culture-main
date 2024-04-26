import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IndividualOfferFormValues,
} from 'components/IndividualOfferForm'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import fullMoreIcon from 'icons/full-more.svg'
import { Select } from 'ui-kit/form/Select/Select'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from '../IndividualOfferForm.module.scss'
import { onVenueChange } from '../UsefulInformations/Venue/Venue'
import buildSubcategoryFields from '../utils/buildSubCategoryFields'
import { getFilteredVenueListBySubcategory } from '../utils/getFilteredVenueList'

import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from './constants'
import { LegacyMusicTypes, MusicTypes } from './MusicTypes'
import { OfferSubtypeTag } from './OfferSubtypeTag/OfferSubtypeTag'
import { ShowTypes } from './ShowTypes'

export interface CategoriesProps {
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  readOnlyFields?: string[]
  showAddVenueBanner: boolean
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
  venueList: VenueListItemResponseModel[]
  isEvent: boolean | null
}

const buildCategoryOptions = (
  categories: CategoryResponseModel[]
): SelectOption[] =>
  categories
    .map((category: CategoryResponseModel) => ({
      value: category.id,
      label: category.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

const buildSubcategoryOptions = (
  subCategories: SubcategoryResponseModel[],
  categoryId: string
): SelectOption[] =>
  buildCategoryOptions(
    subCategories.filter(
      (subCategory: SubcategoryResponseModel) =>
        subCategory.categoryId === categoryId
    )
  )

const Categories = ({
  categories,
  subCategories,
  readOnlyFields = [],
  showAddVenueBanner,
  offerSubtype,
  venueList,
  isEvent,
}: CategoriesProps): JSX.Element => {
  const {
    values: { categoryId, subCategoryFields, offererId },
    setFieldValue,
    handleChange,
  } = useFormikContext<IndividualOfferFormValues>()
  const { setSubcategory } = useIndividualOfferContext()
  const isBookingContactEnabled = useActiveFeature(
    'WIP_MANDATORY_BOOKING_CONTACT'
  )
  const isTitliveGenreEnabled = useActiveFeature(
    'ENABLE_PRO_TITELIVE_MUSIC_GENRES'
  )
  const categoryOptions = buildCategoryOptions(categories)
  const subcategoryOptions = buildSubcategoryOptions(subCategories, categoryId)

  const onSubCategoryChange = async (newSubCategoryId: string) => {
    const newSubcategory = subCategories.find(
      (subcategory) => subcategory.id === newSubCategoryId
    )

    const { subcategoryFields: newSubcategoryFields } = buildSubcategoryFields(
      isBookingContactEnabled,
      newSubcategory
    )
    await setFieldValue('subCategoryFields', newSubcategoryFields)
    await setFieldValue('isDuo', Boolean(newSubcategory?.canBeDuo))

    setSubcategory(newSubcategory)

    if (newSubcategoryFields === subCategoryFields) {
      return
    }

    const fieldsToReset = subCategoryFields.filter(
      (field: string) => !newSubcategoryFields.includes(field)
    )
    fieldsToReset.forEach(async (field: string) => {
      if (field in SUBCATEGORIES_FIELDS_DEFAULT_VALUES) {
        await setFieldValue(
          field,
          SUBCATEGORIES_FIELDS_DEFAULT_VALUES[
            field as keyof typeof SUBCATEGORIES_FIELDS_DEFAULT_VALUES
          ]
        )
      }
    })

    // If there is only one venue available for this subcategory, we select it automatically
    const filteredVenueList = getFilteredVenueListBySubcategory(
      venueList,
      subCategories.find((subcategory) => subcategory.id === newSubCategoryId)
    )
    if (filteredVenueList.length === 1) {
      await setFieldValue('venueId', filteredVenueList[0].id.toString())
      await onVenueChange(
        setFieldValue,
        filteredVenueList,
        filteredVenueList[0].id.toString()
      )
    } else if (filteredVenueList.length > 1) {
      // If there are several venues available for this subcategory,
      // we still need to update the isVenueVirtual field
      // because it is used for form validation
      await setFieldValue(
        'isVenueVirtual',
        filteredVenueList.every((v) => v.isVirtual)
      )
    }
    // If there is no venue no need to update the isVenueVirtual field,
    // the form is not displayed
  }

  const onCategoryChange = async (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
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
    await setFieldValue('subcategoryId', subCategoryId, false)
    await onSubCategoryChange(subCategoryId)
  }

  const hasSubCategory = categoryId !== FORM_DEFAULT_VALUES.categoryId
  const hasMusicType =
    categoryId !== 'LIVRE' && isTitliveGenreEnabled
      ? subCategoryFields.includes('gtl_id')
      : subCategoryFields.includes('musicType')
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
            }}
            svgAlt="Nouvelle fenêtre"
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
          onChange={async (event: React.ChangeEvent<HTMLSelectElement>) => {
            await onCategoryChange(event)
            handleChange(event)
          }}
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
            onChange={async (event: React.ChangeEvent<HTMLSelectElement>) => {
              await onSubCategoryChange(event.target.value)
              handleChange(event)
            }}
          />
        </FormLayout.Row>
      )}

      {hasMusicType &&
        (isTitliveGenreEnabled ? (
          <MusicTypes
            readOnly={readOnlyFields.includes('gtl_id')}
            isEvent={isEvent}
          />
        ) : (
          <LegacyMusicTypes readOnly={readOnlyFields.includes('musicType')} />
        ))}

      {hasShowType && (
        <ShowTypes readOnly={readOnlyFields.includes('showType')} />
      )}
      {showAddVenueBanner && (
        <FormLayout.Row>
          <Callout
            links={[
              {
                href: `/structures/${offererId}/lieux/creation`,
                icon: { src: fullMoreIcon, alt: 'Nouvelle fenêtre, par lieu' },
                label: 'Ajouter un lieu',
              },
            ]}
            variant={CalloutVariant.ERROR}
          >
            Pour créer une offre dans cette catégorie, ajoutez d’abord un lieu à
            votre structure.
          </Callout>
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Categories
