import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOfferStockResponseModel } from 'apiClient/v1'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { StocksEventCreation } from 'screens/IndividualOffer/StocksEventCreation/StocksEventCreation'
import StocksEventEdition from 'screens/IndividualOffer/StocksEventEdition/StocksEventEdition'
import StocksThing from 'screens/IndividualOffer/StocksThing/StocksThing'
import Spinner from 'ui-kit/Spinner/Spinner'

import { serializeStockEvents } from './serializeStockEvents'

const Stocks = (): JSX.Element | null => {
  const { offer, setOffer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const [stockEvents, setStockEvents] = useState<StocksEvent[]>([])
  const [stocks, setStocks] = useState<GetOfferStockResponseModel[]>([])
  const [stockCount, setStockCount] = useState<number>(0)
  const [searchParams] = useSearchParams()
  const page = searchParams.get('page')

  useEffect(() => {
    // we set ignore variable to avoid race conditions
    // see react doc:  https://react.dev/reference/react/useEffect#fetching-data-with-effects
    let ignore = false
    async function loadStocks() {
      if (!offer) {
        return
      }
      const response = await api.getStocks(
        offer.id,
        undefined, // date
        undefined, // time
        undefined, // priceCategoryId
        undefined, // orderBy
        undefined, // orderByDesc
        page ? Number(page) : 1
      )
      if (!ignore) {
        if (offer?.isEvent) {
          setStockEvents(serializeStockEvents(response.stocks))
          setStockCount(response.stock_count)
        } else {
          setStocks(response.stocks)
        }
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
    return () => {
      ignore = true
    }
  }, [page])

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the IndividualOfferWizard
  // to share the offer context
  if (offer === null || !offer.priceCategories) {
    // we don't want to display the spinner when stocks are loading
    // it really looks bad for the stocks pagination
    // (the spinner is displayed each time we change page)
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      offer={offer}
      setOffer={setOffer}
      title={getTitle(mode)}
      mode={mode}
    >
      {offer.isEvent ? (
        mode === OFFER_WIZARD_MODE.CREATION ? (
          <StocksEventCreation
            offer={offer}
            stocks={stockEvents}
            setStocks={setStockEvents}
            stockCount={stockCount}
          />
        ) : (
          <StocksEventEdition
            offer={offer}
            stocks={stockEvents}
            setStocks={setStockEvents}
          />
        )
      ) : (
        <StocksThing offer={offer} stocks={stocks} />
      )}
    </IndivualOfferLayout>
  )
}

export default Stocks
