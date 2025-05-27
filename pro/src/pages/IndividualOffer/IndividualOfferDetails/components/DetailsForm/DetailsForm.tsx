import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
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

import styles from './DetailsForm.module.scss'
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
  categoryStatus: CATEGORY_STATUS
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  isProductBased,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
  categoryStatus,
  displayedImage,
  onImageUpload,
  onImageDelete,
}: DetailsFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const subcategoryId = watch('subcategoryId')
  const { offer } = useIndividualOfferContext()

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const showAddVenueBanner = venuesOptions.length === 0

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER,
      imageCreationStage: 'add image',
    })
  }

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row className={styles['row']}>
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
              <FormLayout.Row className={styles['row']}>
                <Select
                  label="Qui propose l’offre ?"
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  {...register('venueId')}
                  onChange={(e) => {
                    if (isProductBased) {
                      return
                    }

                    setValue('venueId', e.target.value)
                  }}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                  error={errors.venueId?.message}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row className={styles['row']}>
              <TextInput
                count={watch('name').length}
                label="Titre de l’offre"
                maxLength={90}
                {...register('name')}
                error={errors.name?.message}
                required
                disabled={readOnlyFields.includes('name')}
              />
            </FormLayout.Row>
            <FormLayout.Row
              sideComponent={<MarkdownInfoBox />}
              className={styles['row']}
            >
              <TextArea
                label="Description"
                maxLength={10000}
                {...register('description')}
                disabled={readOnlyFields.includes('description')}
                error={errors.description?.message}
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
                className={styles['row']}
              >
                <TextInput
                  label="URL d’accès à l’offre"
                  type="text"
                  description="Format : https://exemple.com"
                  disabled={readOnlyFields.includes('url')}
                  {...register('url')}
                  error={errors.url?.message}
                  required
                />
              </FormLayout.Row>
            )}
          </>
        )}
      </FormLayout.Section>
      <ImageUploaderOffer
        displayedImage={displayedImage}
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        onImageDropOrSelected={logOnImageDropOrSelected}
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
