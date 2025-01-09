import { useFormikContext } from 'formik'
import React, { useState } from 'react'
import { useDebouncedCallback } from 'use-debounce'

import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  SuggestedSubcategoriesResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useSuggestedSubcategoriesAbTest } from 'commons/hooks/useSuggestedSubcategoriesAbTest'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import fullMoreIcon from 'icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildVenueOptions,
  isSubCategoryCD,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { Subcategories } from './Subcategories/Subcategories'
import { SuggestedSubcategories } from './SuggestedSubcategories/SuggestedSubcategories'

const DEBOUNCE_TIME_BEFORE_REQUEST = 400

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  isProductBased: boolean
  filteredVenues: VenueListItemResponseModel[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readonlyFields: string[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  isProductBased,
  filteredVenues,
  filteredCategories,
  filteredSubcategories,
  readonlyFields: readOnlyFields,
  onImageUpload,
  onImageDelete,
  imageOffer,
}: DetailsFormProps): JSX.Element => {
  const areSuggestedSubcategoriesUsed =
    useSuggestedSubcategoriesAbTest(filteredVenues)
  const [hasSuggestionsApiBeenCalled, setHasSuggestionsApiBeenCalled] =
    useState(false)
  const [suggestedSubcategories, setSuggestedSubcategories] = useState<
    SuggestedSubcategoriesResponseModel['subcategoryIds']
  >([])
  const { values, setValues, handleChange, setFieldValue } =
    useFormikContext<DetailsFormValues>()
  const { subcategoryId, description, venueId, name, suggestedSubcategory } =
    values
  const { offer, subCategories } = useIndividualOfferContext()
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const venueOptions = buildVenueOptions(
    filteredVenues,
    areSuggestedSubcategoriesUsed,
    offerAddressEnabled
  )

  async function getSuggestedSubcategories() {
    if (!areSuggestedSubcategoriesUsed && !offer) {
      return
    }

    try {
      const response = await api.getSuggestedSubcategories(
        name,
        description,
        Number(venueId)
      )

      if (response.subcategoryIds.length === 0) {
        throw new Error('No suggested subcategories')
      }

      await setFieldValue('callId', response.callId)
      setSuggestedSubcategories(response.subcategoryIds)
    } catch {
      if (!suggestedSubcategory) {
        await setValues({
          ...values,
          suggestedSubcategory: 'OTHER',
        })
      }
    }

    if (!hasSuggestionsApiBeenCalled) {
      setHasSuggestionsApiBeenCalled(true)
    }
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
    if (areSuggestedSubcategoriesUsed) {
      await debouncedOnChangeGetSuggestedSubcategories()
    }
  }

  const subcategory = subCategories.find((s) => s.id === subcategoryId)

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const showAddVenueBanner =
    !areSuggestedSubcategoriesUsed && venueOptions.length === 0

  const isSuggestedSubcategoryDisplayed =
    areSuggestedSubcategoriesUsed && !offer && !isProductBased

  const showOtherAddVenueBanner =
    areSuggestedSubcategoriesUsed &&
    venueOptions.length === 0 &&
    subcategory?.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row>
            <Callout
              links={[
                {
                  href: `/parcours-inscription/structure`,
                  icon: {
                    src: fullMoreIcon,
                    alt: '',
                  },
                  label: 'Ajouter une structure',
                },
              ]}
              variant={CalloutVariant.ERROR}
            >
              Pour créer une offre dans cette catégorie, ajoutez d’abord une
              structure.
            </Callout>
          </FormLayout.Row>
        )}
        {!showAddVenueBanner && (
          <>
            {venueOptions.length > 1 && (
              <FormLayout.Row>
                <Select
                  label={offerAddressEnabled ? 'Qui propose l’offre ?' : 'Lieu'}
                  name="venueId"
                  options={venueOptions}
                  onChange={async (ev) => {
                    if (isProductBased) {
                      return
                    }

                    await onChangeGetSuggestedSubcategories(ev)
                  }}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venueOptions.length === 1
                  }
                  {...(isSuggestedSubcategoryDisplayed && {
                    'aria-controls': 'suggested-subcategories',
                  })}
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
                {...(isSuggestedSubcategoryDisplayed && {
                  'aria-controls': 'suggested-subcategories',
                })}
              />
            </FormLayout.Row>
            <FormLayout.Row>
              <TextArea
                isOptional
                label="Description"
                maxLength={1000}
                name="description"
                onChange={onChangeGetSuggestedSubcategories}
                disabled={readOnlyFields.includes('description')}
                {...(isSuggestedSubcategoryDisplayed && {
                  'aria-controls': 'suggested-subcategories',
                })}
              />
            </FormLayout.Row>
          </>
        )}
      </FormLayout.Section>
      {isSuggestedSubcategoryDisplayed ? (
        <SuggestedSubcategories
          hasApiBeenCalled={hasSuggestionsApiBeenCalled}
          suggestedSubcategories={suggestedSubcategories}
          readOnlyFields={readOnlyFields}
          filteredCategories={filteredCategories}
          filteredSubcategories={filteredSubcategories}
        />
      ) : (
        !showAddVenueBanner && (
          <Subcategories
            readOnlyFields={readOnlyFields}
            filteredCategories={filteredCategories}
            filteredSubcategories={filteredSubcategories}
          />
        )
      )}
      {isSubCategorySelected && (
        <>
          {showOtherAddVenueBanner ? (
            <FormLayout.Row>
              <Callout
                links={[
                  {
                    href: `/parcours-inscription/structure`,
                    icon: {
                      src: fullMoreIcon,
                      alt: '',
                    },
                    label: 'Ajouter une structure',
                  },
                ]}
                variant={CalloutVariant.ERROR}
              >
                Pour créer une offre dans cette catégorie, ajoutez d’abord une
                structure.
              </Callout>
            </FormLayout.Row>
          ) : (
            <DetailsSubForm
              isEanSearchDisplayed={isEanSearchDisplayed}
              isProductBased={isProductBased}
              isOfferCD={isSubCategoryCD(subcategoryId)}
              readOnlyFields={readOnlyFields}
              onImageUpload={onImageUpload}
              onImageDelete={onImageDelete}
              imageOffer={imageOffer}
            />
          )}
        </>
      )}
    </>
  )
}
