import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MarkdownInfoBox } from 'components/MarkdownInfoBox/MarkdownInfoBox'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import fullMoreIcon from 'icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { ImageUploaderOffer } from './ImageUploaderOffer/ImageUploaderOffer'
import { Subcategories } from './Subcategories/Subcategories'

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  isProductBased: boolean
  venuesOptions: { label: string; value: string }[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readOnlyFields: string[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  imageOffer?: IndividualOfferImage
  categoryStatus: CATEGORY_STATUS
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  isProductBased,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
  onImageUpload,
  onImageDelete,
  imageOffer,
  categoryStatus,
}: DetailsFormProps): JSX.Element => {
  const {
    register,
    watch,
    getValues,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()
  const { subcategoryId } = getValues()
  const { offer } = useIndividualOfferContext()

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const showAddVenueBanner = venuesOptions.length === 0

  const venueIdField = register('venueId')
  const name = watch('name')

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
              Pour créer une offre, vous devez d’abord créer une structure.
            </Callout>
          </FormLayout.Row>
        )}
        {!showAddVenueBanner && (
          <>
            {venuesOptions.length > 1 && (
              <FormLayout.Row>
                <Select
                  label="Qui propose l’offre ?"
                  {...venueIdField}
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  onChange={(ev) => {
                    if (isProductBased) {
                      return
                    }

                    void venueIdField.onChange(ev)
                  }}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                  error={errors.venueId?.message}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row>
              <TextInput
                label="Titre de l’offre"
                maxLength={90}
                {...register('name')}
                error={errors.name?.message}
                count={name.length}
                disabled={readOnlyFields.includes('name')}
              />
            </FormLayout.Row>
            <FormLayout.Row sideComponent={<MarkdownInfoBox />}>
              <TextArea
                asterisk={false}
                label="Description"
                maxLength={1000}
                name="description"
                disabled={readOnlyFields.includes('description')}
              />
            </FormLayout.Row>
            {(categoryStatus === CATEGORY_STATUS.ONLINE ||
              offer?.isDigital) && (
              <FormLayout.Row
                sideComponent={
                  <InfoBox>
                    Lien vers lequel seront renvoyés les bénéficiaires ayant
                    réservé votre offre sur l’application pass Culture.
                  </InfoBox>
                }
              >
                <TextInput
                  label="URL d’accès à l’offre"
                  {...register('url')}
                  description="Format : https://exemple.com"
                  disabled={readOnlyFields.includes('url')}
                />
              </FormLayout.Row>
            )}
          </>
        )}
      </FormLayout.Section>
      <ImageUploaderOffer
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        imageOffer={imageOffer}
        hideActionButtons={isProductBased}
      />
      {!showAddVenueBanner && (
        <Subcategories
          readOnlyFields={readOnlyFields}
          filteredCategories={filteredCategories}
          filteredSubcategories={filteredSubcategories}
        />
      )}
      {isSubCategorySelected && (
        <DetailsSubForm
          isEanSearchDisplayed={isEanSearchDisplayed}
          isProductBased={isProductBased}
          isOfferCD={isSubCategoryCD(subcategoryId)}
          readOnlyFields={readOnlyFields}
        />
      )}
    </>
  )
}
