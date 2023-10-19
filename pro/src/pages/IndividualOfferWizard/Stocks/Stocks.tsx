import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOfferStockResponseModel } from 'apiClient/v1'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { StocksEventCreation } from 'screens/IndividualOffer/StocksEventCreation/StocksEventCreation'
import StocksEventEdition from 'screens/IndividualOffer/StocksEventEdition/StocksEventEdition'
import StocksThing from 'screens/IndividualOffer/StocksThing/StocksThing'
import Spinner from 'ui-kit/Spinner/Spinner'

const Stocks = (): JSX.Element | null => {
  const { offer, setOffer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const [isLoading, setIsLoading] = useState(true)
  const [stocks, setStocks] = useState<GetOfferStockResponseModel[]>([])
  const notify = useNotification()

  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      if (offer?.isEvent && mode === OFFER_WIZARD_MODE.EDITION) {
        try {
          const response = await api.getStocks(offer.id)

          setStocks(response.stocks)
        } catch {
          notify.error(
            'Une erreur est survenue lors du chargement de vos stocks.'
          )
        }
      }
      setIsLoading(false)
    }
    loadData()
  }, [])

  // Here we display a spinner because when the router transitions from
  // Informations form to Stocks form the setOffer after the submit is not
  // propagated yet so there is a quick moment where the offer is null.
  // This is a temporary fix until we use a better pattern than the IndividualOfferWizard
  // to share the offer context
  if (offer === null || isLoading) {
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
          <StocksEventCreation offer={offer} />
        ) : (
          <StocksEventEdition offer={offer} stocks={stocks} />
        )
      ) : (
        <StocksThing offer={offer} />
      )}
    </IndivualOfferLayout>
  )
}

export default Stocks
