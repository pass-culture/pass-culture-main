import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { StocksCalendar } from 'components/IndividualOffer/StocksEventCreation/StocksCalendar/StocksCalendar'
import { StocksEventCreation } from 'components/IndividualOffer/StocksEventCreation/StocksEventCreation'
import { StocksEventEdition } from 'components/IndividualOffer/StocksEventEdition/StocksEventEdition'
import { StocksThing } from 'components/IndividualOffer/StocksThing/StocksThing'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Stocks = (): JSX.Element | null => {
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

  const isEventWithOpeningHoursEnabled = useActiveFeature(
    'WIP_ENABLE_EVENT_WITH_OPENING_HOUR'
  )

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the IndividualOfferWizard
  // to share the offer context
  if (offer === null || !offer.priceCategories) {
    return <Spinner />
  }

  const getStocksLayoutContent = () => {
    if (!offer.isEvent) {
      return <StocksThing offer={offer} />
    }

    if (isEventWithOpeningHoursEnabled) {
      return <StocksCalendar offer={offer} mode={mode} />
    }

    return mode === OFFER_WIZARD_MODE.CREATION ? (
      <StocksEventCreation offer={offer} />
    ) : (
      <StocksEventEdition offer={offer} />
    )
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      {getStocksLayoutContent()}
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Stocks
