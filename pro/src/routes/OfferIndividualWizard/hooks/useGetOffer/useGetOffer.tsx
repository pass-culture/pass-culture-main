import { useCallback, useEffect, useState } from 'react'

import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'

type TUseGetOfferLoading = {
  data?: undefined
  isLoading: true
  error?: undefined
  reloadOffer: () => void
}

type TUseGetOfferSuccess = {
  data?: IOfferIndividual
  isLoading: false
  error?: undefined
  reloadOffer: () => void
}

type TUseGetOfferFailure = {
  data?: undefined
  isLoading: false
  error: {
    message: string
  }
  reloadOffer: () => void
}

const useGetOffer = (
  offerId?: string
): TUseGetOfferLoading | TUseGetOfferSuccess | TUseGetOfferFailure => {
  const [isLoading, setIsLoading] = useState<boolean>(offerId !== undefined)
  const [error, setError] = useState<AdapterFailure<null>>()
  const [offer, setOffer] = useState<IOfferIndividual | undefined>()

  const loadOffer = useCallback(async () => {
    setIsLoading(true)
    const response = await getOfferIndividualAdapter(offerId)
    if (response.isOk) {
      setOffer(response.payload)
    } else {
      setError(response)
    }
    setIsLoading(false)
  }, [offerId])

  useEffect(() => {
    if (offerId) {
      loadOffer()
    } else {
      setOffer(undefined)
      setIsLoading(false)
    }
  }, [offerId])

  if (isLoading === true) {
    return { isLoading, reloadOffer: () => loadOffer }
  }

  if (error !== undefined) {
    return {
      isLoading,
      error: {
        message: error.message,
      },
      reloadOffer: () => loadOffer,
    }
  }

  return {
    data: offer,
    isLoading,
    error: error,
    reloadOffer: () => loadOffer,
  }
}

export default useGetOffer
