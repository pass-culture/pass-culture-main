import React from 'react'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  setInitialFormValues,
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
} from 'new_components/OfferIndividualForm'
import {
  Informations as InformationsScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Offer = (): JSX.Element | null => {
  const { offer, subCategories, offererNames, venueList } =
    useOfferIndividualContext()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const initialValues: IOfferIndividualFormValues =
    offer === null
      ? setDefaultInitialFormValues(
          FORM_DEFAULT_VALUES,
          offererNames,
          offererId,
          venueId,
          venueList
        )
      : setInitialFormValues(offer, subCategories)

  const readOnlyFields = setFormReadOnlyFields(offer)

  return (
    <WizardTemplate>
      <InformationsScreen
        initialValues={initialValues}
        readOnlyFields={readOnlyFields}
      />
    </WizardTemplate>
  )
}

export default Offer
