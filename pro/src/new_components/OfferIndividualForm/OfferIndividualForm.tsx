import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { UsefulInformations } from './UsefulInformations'

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

  return (
    <FormLayout>
      <Categories />
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
    </FormLayout>
  )
}

export default OfferIndividualForm
