import React from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { useGetOffer } from 'core/Offers/adapters'
import { Stocks as StocksScreen } from 'screens/OfferIndividual/Stocks'

const OfferIndividualCreationStocks = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOffer(offerId)

  if (offerIsLoading === true) {
    return <Spinner />
  }

  if (offerError !== undefined) {
    notify.error(offerError.message)
    history.push('/offres')

    return null
  }

  return (
    <div>
      <StocksScreen offer={offer} />
    </div>
  )
}

export default OfferIndividualCreationStocks
