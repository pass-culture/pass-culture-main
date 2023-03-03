import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS, INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import {
  IOfferCategory,
  IOfferIndividualImage,
  IOfferSubCategory,
} from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import { SynchronizedProviderInformation } from 'screens/OfferIndividual/SynchronisedProviderInfos'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { ImageUploaderOffer } from './ImageUploaderOffer'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { OptionDuo } from './OptionDuo'
import { UsefulInformations } from './UsefulInformations'
import { getFilteredVenueList } from './utils/getFilteredVenueList'

export interface IOfferIndividualFormProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  readOnlyFields?: string[]
  imageOffer?: IOfferIndividualImage
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
}: IOfferIndividualFormProps) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { offererId, subcategoryId, venueId },
  } = useFormikContext<IOfferIndividualFormValues>()
  const isPriceCategoriesActive = useActiveFeature(
    'WIP_ENABLE_MULTI_PRICE_STOCKS'
  )

  useScrollToFirstErrorAfterSubmit()

  const filteredVenueList = getFilteredVenueList(
    subcategoryId,
    subCategories,
    venueList
  )

  const showFullForm = subcategoryId.length > 0 && filteredVenueList.length > 0

  const offerSubCategory = subCategories.find(s => s.id === subcategoryId)

  const venue = filteredVenueList.find(v => v.id === venueId)
  const isVenueVirtual = venue?.isVirtual || false

  const areAllVenuesVirtual = venueList
    .filter(v => v.managingOffererId == offererId)
    .every(v => v.isVirtual)

  const showAddVenueBanner =
    offerSubCategory &&
    offerSubCategory.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE &&
    areAllVenuesVirtual

  const { offer } = useOfferIndividualContext()
  const providerName = offer?.lastProviderName

  return (
    <>
      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}

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

          {!isPriceCategoriesActive && (
            <OptionDuo readOnlyFields={readOnlyFields} />
          )}

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
