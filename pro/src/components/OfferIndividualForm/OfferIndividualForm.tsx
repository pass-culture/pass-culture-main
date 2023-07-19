import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { OfferIndividualFormValues } from 'components/OfferIndividualForm'
import { OffererName } from 'core/Offerers/types'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import {
  OfferCategory,
  OfferIndividualImage,
  OfferSubCategory,
} from 'core/Offers/types'
import { OfferIndividualVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { ImageUploaderOffer } from './ImageUploaderOffer'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { UsefulInformations } from './UsefulInformations'
import { getFilteredVenueList } from './utils/getFilteredVenueList'

export interface OfferIndividualFormProps {
  offererNames: OffererName[]
  venueList: OfferIndividualVenue[]
  categories: OfferCategory[]
  subCategories: OfferSubCategory[]
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  readOnlyFields?: string[]
  imageOffer?: OfferIndividualImage
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
}

const OfferIndividualForm = ({
  offererNames,
  venueList,
  categories,
  subCategories,
  readOnlyFields = [],
  onImageUpload,
  onImageDelete,
  imageOffer,
  offerSubtype,
}: OfferIndividualFormProps) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { offererId, subcategoryId, venueId },
  } = useFormikContext<OfferIndividualFormValues>()

  useScrollToFirstErrorAfterSubmit()

  const filteredVenueList = getFilteredVenueList(
    subcategoryId,
    subCategories,
    venueList
  )

  const showFullForm = subcategoryId.length > 0 && filteredVenueList.length > 0

  const offerSubCategory = subCategories.find(s => s.id === subcategoryId)

  const venue = filteredVenueList.find(v => v.id.toString() == venueId)

  const isVenueVirtual = venue?.isVirtual || false

  const matchOffererId = (venue: OfferIndividualVenue) => {
    return venue.managingOffererId.toString() == offererId
  }

  const areAllVenuesVirtual = venueList
    .filter(matchOffererId)
    .every(v => v.isVirtual)

  const showAddVenueBanner =
    offerSubCategory &&
    offerSubCategory.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE &&
    areAllVenuesVirtual

  return (
    <>
      <FormLayout.MandatoryInfo />

      <Categories
        categories={categories}
        subCategories={subCategories}
        readOnlyFields={readOnlyFields}
        showAddVenueBanner={showAddVenueBanner}
        offerSubtype={offerSubtype}
        venueList={venueList}
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

export default OfferIndividualForm
