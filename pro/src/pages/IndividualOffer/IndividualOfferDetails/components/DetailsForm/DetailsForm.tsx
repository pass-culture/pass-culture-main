import type { ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useAccessibilityOptions } from 'commons/hooks/useAccessibilityOptions'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { getAccessibilityInfoFromVenue } from 'commons/utils/getAccessibilityInfoFromVenue'
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
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './DetailsForm.module.scss'
import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { ImageUploaderOffer } from './ImageUploaderOffer/ImageUploaderOffer'
import { Subcategories } from './Subcategories/Subcategories'
import { VideoUploader } from './VideoUploader/VideoUploader'

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  hasSelectedProduct: boolean
  venues: VenueListItemResponseModel[]
  venuesOptions: { label: string; value: string }[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readOnlyFields: string[]
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  withUrlInput: boolean
}

export const DetailsForm = ({
  isEanSearchDisplayed,
  hasSelectedProduct,
  venues,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
  displayedImage,
  onImageUpload,
  onImageDelete,
  withUrlInput,
}: DetailsFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const isVideoEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const {
    formState: { errors },
    register,
    setValue,
    trigger,
    watch,
  } = useFormContext<DetailsFormValues>()

  const subcategoryId = watch('subcategoryId')
  const accessibility = watch('accessibility')

  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )
  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId
  const showAddVenueBanner = venuesOptions.length === 0

  const accessibilityOptionsGroups = useAccessibilityOptions(
    setValue,
    accessibility
  )

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER,
      imageCreationStage: 'add image',
    })
  }

  // TODO (igabriele, 2025-07-16): Use a `watch` flow once the FF is enabled in production.
  const updateVenue = (event: ChangeEvent<HTMLSelectElement>) => {
    if (!isNewOfferCreationFlowFeatureActive && hasSelectedProduct) {
      return
    }

    const venueId = event.target.value
    setValue('venueId', venueId, {
      shouldValidate: true,
    })

    if (!isNewOfferCreationFlowFeatureActive) {
      return
    }

    const venue = venues.find((venue) => venue.id === Number(venueId))
    if (!venue) {
      // TODO (igabriele, 2025-07-16): Handle that more gracefully once we have agreed on how to handle it.
      throw new Error(`Venue with id ${venueId} not found in venues.`)
    }

    const { accessibility } = getAccessibilityInfoFromVenue(venue)
    setValue('accessibility', accessibility)
  }

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row className={styles.row}>
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
              <FormLayout.Row className={styles.row}>
                <Select
                  label="Qui propose l’offre ? *"
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  {...register('venueId', {
                    onChange: updateVenue,
                  })}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                  error={errors.venueId?.message}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row className={styles.row}>
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
              className={styles.row}
            >
              <TextArea
                label="Description"
                maxLength={10000}
                {...register('description')}
                disabled={readOnlyFields.includes('description')}
                error={errors.description?.message}
              />
            </FormLayout.Row>
            {withUrlInput && (
              <FormLayout.Row className={styles.row}>
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
        hideActionButtons={hasSelectedProduct}
        isDisabled={hasSelectedProduct}
      />
      {isVideoEnabled && <VideoUploader />}
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
          isProductBased={hasSelectedProduct}
          isOfferCD={isSubCategoryCD(subcategoryId)}
          readOnlyFields={readOnlyFields}
        />
      )}
      {isNewOfferCreationFlowFeatureActive && accessibilityOptionsGroups && (
        <FormLayout.Section title="Modalités d’accessibilité">
          <FormLayout.Row>
            <CheckboxGroup
              name="accessibility"
              group={accessibilityOptionsGroups}
              disabled={readOnlyFields.includes('accessibility')}
              legend="Cette offre est accessible au public en situation de handicap :"
              onChange={() => trigger('accessibility')}
              required
              error={errors.accessibility?.message}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}
    </>
  )
}
