import React from 'react'
import { useSelector } from 'react-redux'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { UsefulInformations } from './UsefulInformations'
import { useFormikContext } from 'formik'
import { RootState } from 'store/reducers'

interface IOfferIndividualForm {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

const OfferIndividualForm = ({
  offererNames,
  venueList,
}: IOfferIndividualForm) => {
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const { values: { subcategoryId } } = useFormikContext<IOfferIndividualFormValues>()
  const { categories, subCategories } = useSelector(
    (state: RootState) => state.offers.categories
  )

  return (
    <FormLayout>
      <Categories categories={categories} subcategories={subCategories}/>
      {subcategoryId.length > 0 && (
        <>
          <Informations />
          <Image />
          <UsefulInformations
            isUserAdmin={isAdmin}
            offererNames={offererNames}
            venueList={venueList}
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
