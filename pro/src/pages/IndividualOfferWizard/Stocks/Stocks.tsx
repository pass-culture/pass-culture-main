import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { StocksEventCreation } from 'components/IndividualOffer/StocksEventCreation/StocksEventCreation'
import { StocksEventEdition } from 'components/IndividualOffer/StocksEventEdition/StocksEventEdition'
import { StocksThing } from 'components/IndividualOffer/StocksThing/StocksThing'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Stocks = (): JSX.Element | null => {
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the IndividualOfferWizard
  // to share the offer context
  const isLoading = offer === null || !offer.priceCategories

  let children = <Spinner />
  if (!isLoading) {
    if (offer.isEvent) {
      children =
        mode === OFFER_WIZARD_MODE.CREATION ? (
          <StocksEventCreation offer={offer} />
        ) : (
          <StocksEventEdition offer={offer} />
        )
    } else {
      children = <StocksThing offer={offer} />
    }
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      {children}
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Stocks
