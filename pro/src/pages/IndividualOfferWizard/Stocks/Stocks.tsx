import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { StocksEventCreation } from 'components/IndividualOffer/StocksEventCreation/StocksEventCreation'
import { StocksEventEdition } from 'components/IndividualOffer/StocksEventEdition/StocksEventEdition'
import { StocksThing } from 'components/IndividualOffer/StocksThing/StocksThing'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Stocks = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the IndividualOfferWizard
  // to share the offer context
  if (offer === null || !offer.priceCategories) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      {offer.isEvent ? (
        mode === OFFER_WIZARD_MODE.CREATION ? (
          <StocksEventCreation offer={offer} />
        ) : (
          <StocksEventEdition offer={offer} />
        )
      ) : (
        <StocksThing offer={offer} />
      )}
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Stocks
