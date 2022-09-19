import { useFormikContext } from 'formik'
import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { TOffererName } from 'core/Offerers/types'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import BannerAddVenue from 'new_components/Banner/BannerAddVenue'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { useFilteredVenueList } from './hooks'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { OptionDuo } from './OptionDuo'
import { UsefulInformations } from './UsefulInformations'

export interface IOfferIndividualFormProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  readOnlyFields: string[]
}

const OfferIndividualForm = ({
  offererNames,
  venueList,
  categories,
  subCategories,
  readOnlyFields = [],
}: IOfferIndividualFormProps) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { offererId, subcategoryId, venueId },
  } = useFormikContext<IOfferIndividualFormValues>()

  const filteredVenueList = useFilteredVenueList({
    subCategories,
    subcategoryId,
    venueList,
  })

  const offerSubCategory = subCategories.find(s => s.id === subcategoryId)

  const isVenueVirtual =
    filteredVenueList.find(v => v.id === venueId)?.isVirtual || false

  const areAllVenuesVirtual = venueList
    .filter(v => v.managingOffererId == offererId)
    .every(v => v.isVirtual)

  const displayVenueBanner =
    offerSubCategory &&
    offerSubCategory.onlineOfflinePlatform === CATEGORY_STATUS.OFFLINE &&
    areAllVenuesVirtual

  return (
    <>
      <Categories
        categories={categories}
        subCategories={subCategories}
        readOnlyFields={readOnlyFields}
        Banner={displayVenueBanner && <BannerAddVenue offererId={offererId} />}
      />
      {subcategoryId.length > 0 && filteredVenueList.length > 0 && (
        <>
          <Informations readOnlyFields={readOnlyFields} />
          <Image />
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
