import { createContext, useContext } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { OffererHeadLineOfferResponseModel } from 'apiClient/v1'
import { GET_OFFERER_HEADLINE_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'

type IndividualOffersContextValues = {
  headlineOffer: OffererHeadLineOfferResponseModel | null
  upsertHeadlineOffer: (id: number) => Promise<void>
  removeHeadlineOffer: () => Promise<void>
  isHeadlineOfferAllowedForOfferer: boolean
}

const IndividualOffersContext = createContext<IndividualOffersContextValues>({
  headlineOffer: null,
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
  headlineOffer: OffererHeadLineOfferResponseModel | null
}

export function IndividualOffersContextProvider({
  children,
  isHeadlineOfferAllowedForOfferer,
  headlineOffer,
}: IndividualOffersContextProviderProps) {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { mutate } = useSWRConfig()
  const notify = useNotification()

  const upsertHeadlineOffer = async (offerId: number) => {
    try {
      await api.upsertHeadlineOffer({ offerId })
      notify.success('Votre offre a été mise à la une !')
      await mutate([GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId])
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
        headlineOffer,
        upsertHeadlineOffer,
        removeHeadlineOffer,
        isHeadlineOfferAllowedForOfferer,
      }}
    >
      {children}
    </IndividualOffersContext.Provider>
  )
}
