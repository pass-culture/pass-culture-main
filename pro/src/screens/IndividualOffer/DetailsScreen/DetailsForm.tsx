import { useFormikContext } from 'formik'
import React, { useState } from 'react'
import useSWR from 'swr'
import { useDebouncedCallback } from 'use-debounce'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { ImageUploaderOffer } from 'components/IndividualOfferForm/ImageUploaderOffer/ImageUploaderOffer'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { IndividualOfferImage } from 'core/Offers/types'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { DurationInput } from 'ui-kit/form/DurationInput/DurationInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { DEFAULT_DETAILS_FORM_VALUES } from './constants'
import { Subcategories } from './Subcategories/Subcategories'
import { SuggestedSubcategories } from './SuggestedSubcategories/SuggestedSubcategories'
import { DetailsFormValues } from './types'
import { buildShowSubTypeOptions, buildVenueOptions } from './utils'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

type DetailsFormProps = {
  filteredVenues: VenueListItemResponseModel[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readonlyFields: string[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
}

export const DetailsForm = ({
  filteredVenues,
  filteredCategories,
  filteredSubcategories,
  readonlyFields: readOnlyFields,
  onImageUpload,
  onImageDelete,
  imageOffer,
}: DetailsFormProps): JSX.Element => {
  const areSuggestedCategoriesEnabled = useActiveFeature(
    'WIP_SUGGESTED_SUBCATEGORIES'
  )
  const [suggestedSubcategories, setSuggestedSubcategories] = useState<
    string[]
  >([])
  const {
    values: {
      categoryId,
      subcategoryId,
      showType,
      subcategoryConditionalFields,
      description,
      venueId,
      name,
    },
    handleChange,
  } = useFormikContext<DetailsFormValues>()

  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )

  const musicTypesOptions = musicTypesQuery.data.map((data) => ({
    value: data.gtl_id,
    label: data.label,
  }))
  const showTypesOptions = showOptionsTree
    .map((data) => ({
      label: data.label,
      value: data.code.toString(),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  const showSubTypeOptions = buildShowSubTypeOptions(showType)

  const venueOptions = buildVenueOptions(filteredVenues)

  const artisticInformationsFields = [
    'speaker',
    'author',
    'visa',
    'stageDirector',
    'performer',
    'ean',
    'durationMinutes',
    'showType',
    'gtl_id',
  ]

  const displayArtisticInformations = artisticInformationsFields.some((field) =>
    subcategoryConditionalFields.includes(field)
  )

  const splitFormEnabled = useActiveFeature('WIP_SPLIT_OFFER')
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  // Books have a gtl_id field, other categories have a musicType field
  const hasMusicType =
    categoryId !== 'LIVRE'
      ? subcategoryConditionalFields.includes('gtl_id')
      : subcategoryConditionalFields.includes('musicType')

  async function getSuggestedSubcategories() {
    if (!areSuggestedCategoriesEnabled) {
      return
    }
    const response = await api.getSuggestedSubcategories(
      name,
      description,
      Number(venueId)
    )
    setSuggestedSubcategories(response.subcategoryIds)
  }

  const debouncedOnChangeGetSuggestedSubcategories = useDebouncedCallback(
    getSuggestedSubcategories,
    DEBOUNCE_TIME_BEFORE_REQUEST
  )

  async function onChangeGetSuggestedSubcategories(
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    handleChange(e)
    await debouncedOnChangeGetSuggestedSubcategories()
  }

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  return (
    <>
      <FormLayout.Section title="A propos de votre offre">
        {splitFormEnabled && (
          <FormLayout.Row>
            <Select
              label={offerAddressEnabled ? 'Qui propose l’offre ?' : 'Lieu'}
              name="venueId"
              options={venueOptions}
              onChange={onChangeGetSuggestedSubcategories}
              disabled={
                readOnlyFields.includes('venueId') || venueOptions.length === 1
              }
            />
          </FormLayout.Row>
        )}
        <FormLayout.Row>
          <TextInput
            countCharacters
            label="Titre de l’offre"
            maxLength={90}
            name="name"
            onChange={onChangeGetSuggestedSubcategories}
            disabled={readOnlyFields.includes('name')}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextArea
            countCharacters
            isOptional
            label="Description"
            maxLength={1000}
            name="description"
            onChange={onChangeGetSuggestedSubcategories}
            disabled={readOnlyFields.includes('description')}
          />
        </FormLayout.Row>
        {!splitFormEnabled && (
          <FormLayout.Row>
            <Select
              label={offerAddressEnabled ? 'Qui propose l’offre ?' : 'Lieu'}
              name="venueId"
              options={venueOptions}
              onChange={onChangeGetSuggestedSubcategories}
              disabled={
                readOnlyFields.includes('venueId') || venueOptions.length === 1
              }
            />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
      {areSuggestedCategoriesEnabled ? (
        suggestedSubcategories.length > 0 && (
          <SuggestedSubcategories
            suggestedSubcategories={suggestedSubcategories}
            readOnlyFields={readOnlyFields}
            filteredCategories={filteredCategories}
            filteredSubcategories={filteredSubcategories}
          />
        )
      ) : (
        <Subcategories
          readOnlyFields={readOnlyFields}
          filteredCategories={filteredCategories}
          filteredSubcategories={filteredSubcategories}
        />
      )}
      {isSubCategorySelected && (
        <>
          <ImageUploaderOffer
            onImageUpload={onImageUpload}
            onImageDelete={onImageDelete}
            imageOffer={imageOffer}
          />

          {displayArtisticInformations && (
            <FormLayout.Section title="Informations artistiques">
              {hasMusicType && (
                <FormLayout.Row>
                  <Select
                    label="Genre musical"
                    name="gtl_id"
                    options={musicTypesOptions}
                    defaultOption={{
                      label: 'Choisir un genre musical',
                      value: DEFAULT_DETAILS_FORM_VALUES.gtl_id,
                    }}
                    disabled={readOnlyFields.includes('gtl_id')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('showType') && (
                <>
                  <FormLayout.Row>
                    <Select
                      label="Type de spectacle"
                      name="showType"
                      options={showTypesOptions}
                      defaultOption={{
                        label: 'Choisir un type de spectacle',
                        value: DEFAULT_DETAILS_FORM_VALUES.showType,
                      }}
                      disabled={readOnlyFields.includes('showType')}
                    />
                  </FormLayout.Row>
                  <FormLayout.Row>
                    <Select
                      label="Sous-type"
                      name="showSubType"
                      options={showSubTypeOptions}
                      defaultOption={{
                        label: 'Choisir un sous-type',
                        value: DEFAULT_DETAILS_FORM_VALUES.showSubType,
                      }}
                      disabled={readOnlyFields.includes('showSubType')}
                    />
                  </FormLayout.Row>
                </>
              )}
              {subcategoryConditionalFields.includes('speaker') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Intervenant"
                    maxLength={1000}
                    name="speaker"
                    disabled={readOnlyFields.includes('speaker')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('author') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Auteur"
                    maxLength={1000}
                    name="author"
                    disabled={readOnlyFields.includes('author')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('visa') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Visa d’exploitation"
                    maxLength={1000}
                    name="visa"
                    disabled={readOnlyFields.includes('visa')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('stageDirector') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Metteur en scène"
                    maxLength={1000}
                    name="stageDirector"
                    disabled={readOnlyFields.includes('stageDirector')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('performer') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="Interprète"
                    maxLength={1000}
                    name="performer"
                    disabled={readOnlyFields.includes('performer')}
                  />
                </FormLayout.Row>
              )}
              {subcategoryConditionalFields.includes('ean') && (
                <FormLayout.Row>
                  <TextInput
                    isOptional
                    label="EAN-13 (European Article Numbering)"
                    countCharacters
                    name="ean"
                    maxLength={13}
                    disabled={readOnlyFields.includes('ean')}
                  />
                </FormLayout.Row>
              )}

              {subcategoryConditionalFields.includes('durationMinutes') && (
                <FormLayout.Row>
                  <DurationInput
                    isOptional
                    label={'Durée'}
                    name="durationMinutes"
                    disabled={readOnlyFields.includes('durationMinutes')}
                  />
                </FormLayout.Row>
              )}
            </FormLayout.Section>
          )}
        </>
      )}
    </>
  )
}
