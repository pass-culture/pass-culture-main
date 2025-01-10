import { createContext, useContext, useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GET_OFFERER_HEADLINE_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'

type IndividualOffersContextValues = {
  headlineOfferId: number | null
  upsertHeadlineOffer: (id: number) => Promise<void>
  removeHeadlineOffer: () => Promise<void>
  isHeadlineOfferAllowedForOfferer: boolean
}

const IndividualOffersContext = createContext<IndividualOffersContextValues>({
  headlineOfferId: null,
  upsertHeadlineOffer: async () => {},
  removeHeadlineOffer: async () => {},
  isHeadlineOfferAllowedForOfferer: false,
})

export const useIndividualOffersContext = () => {
  return useContext(IndividualOffersContext)
}

type IndividualOffersContextProviderProps = {
  children: React.ReactNode
  isHeadlineOfferAllowedForOfferer: boolean
}

export function IndividualOffersContextProvider({
  children,
  isHeadlineOfferAllowedForOfferer,
}: IndividualOffersContextProviderProps) {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [headlineOfferId, setHeadlineOfferId] = useState<number | null>(null)
  const isHeadlineOfferEnabled = useActiveFeature('WIP_HEADLINE_OFFER')
  const { mutate } = useSWRConfig()
  const notify = useNotification()

  useSWR(
    selectedOffererId && isHeadlineOfferEnabled
      ? [GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId]
      : null,
    ([, offererId]) => api.getOffererHeadlineOffer(offererId),
    {
      onError: (error) => {
        if (error.status === 404) {
          setHeadlineOfferId(null)
        } else {
          throw error
        }
      },
      onSuccess: (data) => setHeadlineOfferId(data.id),
      shouldRetryOnError: false,
    }
  )

  const upsertHeadlineOffer = async (offerId: number) => {
    try {
      await api.upsertHeadlineOffer({ offerId })
      notify.success('Votre offre à bien été mise à la une !')
      await mutate([GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId])
      setHeadlineOfferId(offerId)
    } catch {
      notify.error(
        'Une erreur s’est produite lors de l’ajout de votre offre à la une'
      )
    }
  }

  const removeHeadlineOffer = async () => {
    if (selectedOffererId) {
      try {
        await api.deleteHeadlineOffer({ offererId: selectedOffererId })
        notify.success('Votre offre n’est plus à la une')
        await mutate([GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId])
        setHeadlineOfferId(null)
      } catch {
        notify.error(
          'Une erreur s’est produite lors du retrait de votre offre à la une'
        )
      }
    }
  }

  return (
    <IndividualOffersContext.Provider
      value={{
        headlineOfferId,
        upsertHeadlineOffer,
        removeHeadlineOffer,
        isHeadlineOfferAllowedForOfferer,
      }}
    >
      {children}
    </IndividualOffersContext.Provider>
  )
}
