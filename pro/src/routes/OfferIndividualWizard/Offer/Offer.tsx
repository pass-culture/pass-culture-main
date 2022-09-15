import React from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { BannerCreateOfferAdmin } from 'new_components/Banner'
import {
  setInitialFormValues,
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setDefaultInitialFormValues,
  setFormReadOnlyFields,
} from 'new_components/OfferIndividualForm'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import {
  Informations as InformationsScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const Offer = (): JSX.Element | null => {
  const isCreation = useIsCreation()
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
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
  const showAdminCreationBanner = isAdmin && isCreation && !offererId
  return (
    <WizardTemplate>
      {showAdminCreationBanner ? (
        <BannerCreateOfferAdmin />
      ) : (
        <InformationsScreen
          initialValues={initialValues}
          readOnlyFields={readOnlyFields}
        />
      )}
    </WizardTemplate>
  )
}

export default Offer
