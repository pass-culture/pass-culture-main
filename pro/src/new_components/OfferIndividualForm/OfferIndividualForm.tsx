import React from 'react'

import FormLayout from 'new_components/FormLayout'

import { Accessibility } from './Accessibility'
import { Categories } from './Categories'
import { ExternalLink } from './ExternalLink'
import { Image } from './Image'
import { Informations } from './Informations'
import { Notifications } from './Notifications'
import { Venue } from './Venue'

const OfferIndividualForm = () => {
  return (
    <FormLayout>
      <Categories />
      <Informations />
      <Image />
      <Venue />
      <Accessibility />
      <ExternalLink />
      <Notifications />
    </FormLayout>
  )
}

export default OfferIndividualForm
