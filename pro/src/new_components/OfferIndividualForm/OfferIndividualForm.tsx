import React from 'react'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { Venue } from './Venue'

interface IOfferIndividualForm {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

const OfferIndividualForm = ({
  offererNames,
  venueList,
}: IOfferIndividualForm) => {
  return (
    <FormLayout>
      <Categories />
      <Informations />
      <Image />

      <FormLayout.Section
        title="Informations pratiques"
        description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
      >
        <Venue offererNames={offererNames} venueList={venueList} />
      </FormLayout.Section>

      <Accessibility />
      <ExternalLink />
      <Notifications />
    </FormLayout>
  )
}

export default OfferIndividualForm
