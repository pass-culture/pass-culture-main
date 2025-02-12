import { createContext, useContext, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import useSWR, { useSWRConfig } from 'swr'


import { api } from 'apiClient/api'
import { OffererHeadLineOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFERER_HEADLINE_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { storageAvailable } from 'commons/utils/storageAvailable'

export const LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY = 'headlineOfferBannerClosed'

type UpsertHeadlineOfferParams = {
  offerId: number
  context: {
    actionType: string
    requiredImageUpload?: boolean
  }
}

type IndividualOffersContextValues = {
  headlineOffer: OffererHeadLineOfferResponseModel | null
  upsertHeadlineOffer: (params: UpsertHeadlineOfferParams) => Promise<void>
  removeHeadlineOffer: () => Promise<void>
  isHeadlineOfferBannerOpen: boolean
  closeHeadlineOfferBanner: () => void
  isHeadlineOfferAllowedForOfferer: boolean
}

const IndividualOffersContext = createContext<IndividualOffersContextValues>({
  headlineOffer: null,
  upsertHeadlineOffer: async () => {},
  removeHeadlineOffer: async () => {},
  isHeadlineOfferBannerOpen: true,
  closeHeadlineOfferBanner: () => {},
  isHeadlineOfferAllowedForOfferer: false,
})

export const useIndividualOffersContext = () => {
  return useContext(IndividualOffersContext)
}

export type IndividualOffersContextProviderProps = {
  children: React.ReactNode
  isHeadlineOfferAllowedForOfferer: boolean
}

export function IndividualOffersContextProvider({
  children,
  isHeadlineOfferAllowedForOfferer,
}: IndividualOffersContextProviderProps) {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [headlineOffer, setHeadlineOffer] =
    useState<OffererHeadLineOfferResponseModel | null>(null)
  const initialIsHeadlineOfferBannerOpen = storageAvailable('localStorage') &&
    localStorage.getItem(LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY) === null
  const [
    isHeadlineOfferBannerOpen,
    setIsHeadlineOfferBannerOpen
  ] = useState(initialIsHeadlineOfferBannerOpen)
  const isHeadlineOfferEnabled = useActiveFeature('WIP_HEADLINE_OFFER')
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  useSWR(
    selectedOffererId && isHeadlineOfferEnabled
      ? [GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId]
      : null,
    ([, offererId]) => api.getOffererHeadlineOffer(offererId),
    {
      onError: (error) => {
        if (error.status === 404) {
          setHeadlineOffer(null)
        } else {
          throw error
        }
      },
      onSuccess: (data) => setHeadlineOffer(data),
      shouldRetryOnError: false,
    }
  )

  const closeHeadlineOfferBanner = () => {
    setIsHeadlineOfferBannerOpen(false)
    if (storageAvailable('localStorage')) {
      localStorage.setItem(LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY, 'true')
    }
  }

  const upsertHeadlineOffer = async ({
    offerId,
    context,
  }: UpsertHeadlineOfferParams) => {
    try {
      await api.upsertHeadlineOffer({ offerId })
      notify.success('Votre offre a été mise à la une !')
      await mutate([GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId])

      logEvent(Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
        from: location.pathname,
        actionType: context.actionType,
        requiredImageUpload: !!context.requiredImageUpload,
      })

      if (isHeadlineOfferBannerOpen) {
        closeHeadlineOfferBanner()
      }
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

        logEvent(Events.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
          from: location.pathname,
          actionType: 'delete',
        })
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
        isHeadlineOfferBannerOpen,
        closeHeadlineOfferBanner,
        isHeadlineOfferAllowedForOfferer,
      }}
    >
      {children}
    </IndividualOffersContext.Provider>
  )
}
