import { useFormikContext } from 'formik'
import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { TOffererName } from 'core/Offerers/types'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { useFilteredVenueList } from './hooks'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { UsefulInformations } from './UsefulInformations'

interface IOfferIndividualForm {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
}

const OfferIndividualForm = ({
  offererNames,
  venueList,
  categories,
  subCategories,
}: IOfferIndividualForm) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const {
    values: { subcategoryId },
  } = useFormikContext<IOfferIndividualFormValues>()

  const filteredVenueList = useFilteredVenueList({
    subCategories,
    subcategoryId,
    venueList,
  })

  return (
    <FormLayout>
      <Categories categories={categories} subCategories={subCategories} />

      {/* @TODO : display reimbursment banner */}
      {/* @TODO : display create venue banner */}
      {/* @TODO : display physical offers banner */}

      {subcategoryId.length > 0 && filteredVenueList.length > 0 && (
        <>
          <Informations />
          <Image />
          <UsefulInformations
            isUserAdmin={isAdmin}
            offererNames={offererNames}
            venueList={filteredVenueList}
          />
          <Accessibility />
          <ExternalLink />
          <Notifications />
        </>
      )}
    </FormLayout>
  )
}

export default OfferIndividualForm
