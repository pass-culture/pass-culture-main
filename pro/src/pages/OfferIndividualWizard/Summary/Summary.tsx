/* istanbul ignore file: DEBT, TO FIX */
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

interface ISummaryProps {
  isOfferV2?: boolean
}

// FIX ME: remove isOfferV2 props when removing OFFER_FORM_V3 FF
const Summary = ({ isOfferV2 = false }: ISummaryProps): JSX.Element | null => {
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

  // FIX ME: when OFFER_FORM_V3 is removed, it will be only string | undefined
  let title: string | undefined | null = undefined
  if (isOfferV2) {
    title = null
  } else if (mode === OFFER_WIZARD_MODE.EDITION) {
    title = 'Récapitulatif'
  }
  return (
    <WizardTemplate
      title={title}
      withStepper={!isOfferV2 && mode !== OFFER_WIZARD_MODE.EDITION}
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
        formOfferV2={isOfferV2}
      />
    </WizardTemplate>
  )
}

export default Summary
