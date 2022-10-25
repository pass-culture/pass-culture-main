/* istanbul ignore file: DEBT, TO FIX */
import React from 'react'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { useOfferWizardMode } from 'hooks'
import PageTitle from 'new_components/PageTitle/PageTitle'
import {
  Summary as SummaryScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

import { serializePropsFromOfferIndividual } from '.'

interface ISummaryProps {
  isOfferV2?: boolean
}

const Summary = ({ isOfferV2 = false }: ISummaryProps): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const {
    offer: contextOffer,
    categories,
    subCategories,
  } = useOfferIndividualContext()
  // FIXME : we should not need  as IOfferIndividual cause parent route would redirect on offer loading error
  const offer = contextOffer as IOfferIndividual
  const {
    providerName,
    offer: offerData,
    stockThing,
    stockEventList,
    preview,
  } = serializePropsFromOfferIndividual(
    offer as IOfferIndividual,
    categories,
    subCategories
  )

  return (
    <WizardTemplate
      title={isOfferV2 ? null : 'Récapitulatif'}
      withStepper={mode !== OFFER_WIZARD_MODE.EDITION}
    >
      <PageTitle title="Récapitulatif" />
      <SummaryScreen
        offerId={offer.id}
        providerName={providerName}
        offer={offerData}
        stockThing={stockThing}
        stockEventList={stockEventList}
        subCategories={subCategories}
        preview={preview}
        formOfferV2
      />
    </WizardTemplate>
  )
}

export default Summary
