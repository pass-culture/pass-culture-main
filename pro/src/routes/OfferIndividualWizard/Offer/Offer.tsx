import React from 'react'
import { useLocation } from 'react-router'

import useCurrentUser from 'components/hooks/useCurrentUser'
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
import { parse } from 'utils/query-string'
const Offer = (): JSX.Element | null => {
  const isCreation = useIsCreation()
  const {
    currentUser: { isAdmin },
  } = useCurrentUser()
  const { offer, subCategories, offererNames, venueList } =
    useOfferIndividualContext()

  const { search } = useLocation()
  const { structure: offererId, lieu: venueId } = parse(search)

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

  const readOnlyFields = setFormReadOnlyFields(offer, isAdmin)
  const showAdminCreationBanner = isAdmin && isCreation && !(offererId || offer)
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
