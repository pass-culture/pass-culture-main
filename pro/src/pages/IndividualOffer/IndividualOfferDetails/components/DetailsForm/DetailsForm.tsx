import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { MarkdownInfoBox } from 'components/MarkdownInfoBox/MarkdownInfoBox'
import fullMoreIcon from 'icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
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
  const form = useFormContext<DetailsFormValues>()

  const subcategoryId = form.watch('subcategoryId')

  const { offer } = useIndividualOfferContext()

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const showAddVenueBanner = venuesOptions.length === 0

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
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  {...form.register('venueId')}
                  onChange={(e) => {
                    if (isProductBased) {
                      return
                    }

                    form.setValue('venueId', e.target.value)
                  }}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row>
              <TextInput
                count={form.watch('name').length}
                label="Titre de l’offre"
                maxLength={90}
                {...form.register('name')}
                required
                disabled={readOnlyFields.includes('name')}
              />
            </FormLayout.Row>
            {/* <FormLayout.Row sideComponent={<MarkdownInfoBox />}>
              <TextArea
                isOptional
                label="Description"
                maxLength={1000}
                name="description"
                onChange={(e) => form.setValue('description', e.target.value)}
                disabled={readOnlyFields.includes('description')}
              />
            </FormLayout.Row> */}
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
                  type="text"
                  description="Format : https://exemple.com"
                  disabled={readOnlyFields.includes('url')}
                  {...form.register('url')}
                  required
                />
              </FormLayout.Row>
            )}
          </>
        )}
      </FormLayout.Section>
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
          onImageUpload={onImageUpload}
          onImageDelete={onImageDelete}
          imageOffer={imageOffer}
        />
      )}
    </>
  )
}
