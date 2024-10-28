import { useFormikContext } from 'formik'
import React from 'react'

import {
  CategoryResponseModel,
  GetOffererNameResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { OfferLocation } from 'pages/IndividualOffer/components/OfferLocation/OfferLocation'
import { ImageUploaderOffer } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/components/ImageUploaderOffer/ImageUploaderOffer'

import { getFilteredVenueListBySubcategory } from '../../../IndividualOfferDetails/commons/getFilteredVenueList'

import { Accessibility } from './Accessibility/Accessibility'
import { Categories } from './Categories/Categories'
import { Informations } from './Informations/Informations'
import { Notifications } from './Notifications/Notifications'
import { UsefulInformations } from './UsefulInformations/UsefulInformations'

export interface IndividualOfferFormProps {
  offererNames: GetOffererNameResponseModel[]
  venueList: VenueListItemResponseModel[]
  categories: CategoryResponseModel[]
  subCategories: SubcategoryResponseModel[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  readOnlyFields?: string[]
  imageOffer?: IndividualOfferImage
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
  isEvent: boolean | null
}

export const IndividualOfferForm = ({
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

  const matchOffererId = (venue: VenueListItemResponseModel) => {
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

  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  return (
    <>
      <ScrollToFirstErrorAfterSubmit />

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

          {offerAddressEnabled && !isVenueVirtual && (
            <OfferLocation venue={venue} />
          )}

          <Accessibility readOnlyFields={readOnlyFields} />

          <Notifications
            venueBookingEmail={venue?.bookingEmail}
            readOnlyFields={readOnlyFields}
          />
        </>
      )}
    </>
  )
}
