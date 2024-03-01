import { useFormikContext } from 'formik'
import React from 'react'

import {
  CategoryResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import { IndividualOfferImage } from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { ImageUploaderOffer } from './ImageUploaderOffer'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { UsefulInformations } from './UsefulInformations'
import { getFilteredVenueListBySubcategory } from './utils/getFilteredVenueList'

export interface IndividualOfferFormProps {
  offererNames: GetOffererNameResponseModel[]
  venueList: IndividualOfferVenueItem[]
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  readOnlyFields?: string[]
  imageOffer?: IndividualOfferImage
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
  isEvent: boolean | null
}

const IndividualOfferForm = ({
  offererNames,
  venueList,
  categories,
  subCategories,
  readOnlyFields = [],
  onImageUpload,
  onImageDelete,
  imageOffer,
  offerSubtype,
  isEvent,
}: IndividualOfferFormProps) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { offererId, subcategoryId, venueId },
  } = useFormikContext<IndividualOfferFormValues>()

  useScrollToFirstErrorAfterSubmit()

  const offerSubCategory = subCategories.find((s) => s.id === subcategoryId)
  const filteredVenueList = getFilteredVenueListBySubcategory(
    venueList,
    offerSubCategory
  )

  const showFullForm = subcategoryId.length > 0 && filteredVenueList.length > 0

  const venue = filteredVenueList.find((v) => v.id.toString() === venueId)

  // we use venue is virtual here because we cannot infer it from the offerSubCategory
  // because of CATEGORY_STATUS.ONLINE_OR_OFFLINE who can be both virtual or not
  const isVenueVirtual = venue?.isVirtual || false

  const matchOffererId = (venue: IndividualOfferVenueItem) => {
    return venue.managingOffererId.toString() === offererId
  }

  const areAllVenuesVirtual = filteredVenueList
    .filter(matchOffererId)
    .every((v) => v.isVirtual)

  // we show the add venue banner only if we have offererId so the link is not broken
  const showAddVenueBanner =
    offerSubCategory &&
    offerSubCategory.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE &&
    areAllVenuesVirtual &&
    offererId

  return (
    <>
      <FormLayout.MandatoryInfo />

      <Categories
        categories={categories}
        subCategories={subCategories}
        readOnlyFields={readOnlyFields}
        showAddVenueBanner={Boolean(showAddVenueBanner)}
        offerSubtype={offerSubtype}
        // subcategory change will recompute the venue list
        // so we need to pass the full venue list here
        venueList={venueList}
        isEvent={isEvent}
      />
      {showFullForm && (
        <>
          <Informations readOnlyFields={readOnlyFields} />
          <ImageUploaderOffer
            onImageUpload={onImageUpload}
            onImageDelete={onImageDelete}
            imageOffer={imageOffer}
          />

          <UsefulInformations
            isUserAdmin={isAdmin}
            offererNames={offererNames}
            venueList={filteredVenueList}
            offerSubCategory={offerSubCategory}
            isVenueVirtual={isVenueVirtual}
            readOnlyFields={readOnlyFields}
          />

          <Accessibility readOnlyFields={readOnlyFields} />

          <ExternalLink readOnlyFields={readOnlyFields} />

          <Notifications
            venueBookingEmail={venue?.bookingEmail}
            readOnlyFields={readOnlyFields}
          />
        </>
      )}
    </>
  )
}

export default IndividualOfferForm
