import { useHistory, useParams } from 'react-router'

import React from 'react'
import Spinner from 'components/layout/Spinner'
import { Stocks as StocksScreen } from 'screens/OfferIndividual/Stocks'
import { useGetOffer } from 'core/Offers/adapters'
import useNotification from 'components/hooks/useNotification'

const OfferIndividualCreationStocks = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOffer(offerId)

  if (offerError !== undefined) {
    notify.error(offerError)
    history.push('/offers')

    return null
  }

  if (offerIsLoading) {
    return <Spinner />
  }

  return (
    <div>
      <StocksScreen offer={offer} />
    </div>
  )
}

export default OfferIndividualCreationStocks
