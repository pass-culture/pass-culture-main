import React from 'react'

import PageTitle from 'components/PageTitle/PageTitle'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { useOfferWizardMode } from 'hooks'
import {
  Summary as SummaryScreen,
  Template as WizardTemplate,
} from 'screens/OfferIndividual'

import { serializePropsFromOfferIndividual } from '.'

const Summary = (): JSX.Element | null => {
  const {
    offer: contextOffer,
    categories,
    subCategories,
  } = useOfferIndividualContext()
  // FIXME : we should not need  as IOfferIndividual cause parent route would redirect on offer loading error
  const offer = contextOffer as IOfferIndividual
  const mode = useOfferWizardMode()
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

  let title: string | undefined = undefined
  if (mode === OFFER_WIZARD_MODE.EDITION) {
    title = 'Récapitulatif'
  }
  return (
    <WizardTemplate
      title={title}
      withStepper={mode !== OFFER_WIZARD_MODE.EDITION}
    >
      <PageTitle title="Récapitulatif" />
      <SummaryScreen
        offerId={offer.id}
        nonHumanizedOfferId={offer.nonHumanizedId}
        providerName={providerName}
        offer={offerData}
        stockThing={stockThing}
        stockEventList={stockEventList}
        subCategories={subCategories}
        preview={preview}
      />
    </WizardTemplate>
  )
}

export default Summary
