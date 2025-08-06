import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { EventCancellationBanner } from '@/components/EventCancellationBanner/EventCancellationBanner'
import { StocksCalendar } from '@/components/IndividualOffer/StocksEventCreation/StocksCalendar/StocksCalendar'
import { StocksThing } from '@/components/IndividualOffer/StocksThing/StocksThing'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export const Stocks = (): JSX.Element | null => {
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const mode = useOfferWizardMode()

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

    return (
      <>
        <EventCancellationBanner offer={offer} />
        <StocksCalendar offer={offer} mode={mode} />
      </>
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

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Stocks
