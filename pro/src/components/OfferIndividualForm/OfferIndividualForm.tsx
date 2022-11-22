import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import {
  IOfferCategory,
  IOfferIndividualImage,
  IOfferSubCategory,
} from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useScrollToFirstErrorAfterSubmit } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { useFilteredVenueList, useShowFullForm } from './hooks'
import { ImageUploaderOffer } from './ImageUploaderOffer'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { OptionDuo } from './OptionDuo'
import { UsefulInformations } from './UsefulInformations'

export interface IOfferIndividualFormProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  onImageDelete: () => Promise<void>
  readOnlyFields?: string[]
  imageOffer?: IOfferIndividualImage
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
}: IOfferIndividualFormProps) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { offererId, subcategoryId, venueId },
  } = useFormikContext<IOfferIndividualFormValues>()

  useScrollToFirstErrorAfterSubmit()

  const filteredVenueList = useFilteredVenueList({
    subCategories,
    subcategoryId,
    venueList,
  })

  const showFullForm = useShowFullForm(subcategoryId, filteredVenueList)

  const offerSubCategory = subCategories.find(s => s.id === subcategoryId)

  const isVenueVirtual =
    filteredVenueList.find(v => v.id === venueId)?.isVirtual || false

  const areAllVenuesVirtual = venueList
    .filter(v => v.managingOffererId == offererId)
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
          <OptionDuo />
          <ExternalLink />
          <Notifications />
        </>
      )}
    </>
  )
}

export default OfferIndividualForm
