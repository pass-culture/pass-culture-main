import React from 'react'

import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

const OfferIndividualCreationInformations = (): JSX.Element => {
  return (
    <div>
      <InformationsScreen initialValues={FORM_DEFAULT_VALUES} />
    </div>
  )
}

export default OfferIndividualCreationInformations
