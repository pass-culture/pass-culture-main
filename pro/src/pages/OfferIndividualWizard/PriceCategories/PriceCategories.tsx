import React from 'react'
import { useNavigate } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import {
  PriceCategories as PriceCategoriesScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

const PriceCategories = (): JSX.Element | null => {
  const { offer } = useOfferIndividualContext()
  const navigate = useNavigate()

  // if we've no offer, we are redirect from parent route.
  /* istanbul ignore next: DEBT, TO FIX */
  if (offer === null) {
    navigate(
      getOfferIndividualUrl({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode: OFFER_WIZARD_MODE.CREATION,
      })
    )
    return null
  }

  return (
    <WizardTemplate>
      <PriceCategoriesScreen offer={offer} />
    </WizardTemplate>
  )
}

export default PriceCategories
