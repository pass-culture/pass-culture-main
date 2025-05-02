import { createContext, useContext, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { HeadLineOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_OFFERER_HEADLINE_OFFER_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { storageAvailable } from 'commons/utils/storageAvailable'

export const LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY =
  'headlineOfferBannerClosed'

type UpsertHeadlineOfferParams = {
  offerId: number
  context: {
    actionType: string
    requiredImageUpload?: boolean
  }
}

type HeadlineOfferContextValues = {
  headlineOffer: HeadLineOfferResponseModel | null
  upsertHeadlineOffer: (params: UpsertHeadlineOfferParams) => Promise<void>
  removeHeadlineOffer: () => Promise<void>
  isHeadlineOfferBannerOpen: boolean
  closeHeadlineOfferBanner: () => void
  isHeadlineOfferAllowedForOfferer: boolean
}

const HeadlineOfferContext = createContext<HeadlineOfferContextValues>({
  headlineOffer: null,
  upsertHeadlineOffer: async () => {},
  removeHeadlineOffer: async () => {},
  isHeadlineOfferBannerOpen: true,
  closeHeadlineOfferBanner: () => {},
  isHeadlineOfferAllowedForOfferer: false,
})

export const useHeadlineOfferContext = () => {
  return useContext(HeadlineOfferContext)
}

type HeadlineOfferContextProviderProps = { children: React.ReactNode }

export function HeadlineOfferContextProvider({
  children,
}: HeadlineOfferContextProviderProps) {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const { data } = useSWR([GET_VENUES_QUERY_KEY, selectedOffererId], () =>
    api.getVenues(null, null, selectedOffererId)
  )
  const nonVirtualVenues =
    data?.venues.filter((venue) => !venue.isVirtual) || []
  const isHeadlineOfferAllowedForOfferer =
    nonVirtualVenues.length === 1 && nonVirtualVenues[0].isPermanent
  const wasHeadlineOfferPreviouslyClosed =
    storageAvailable('localStorage') &&
    localStorage.getItem(LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY) !==
      null
  const initialIsHeadlineOfferBannerOpen =
    isHeadlineOfferAllowedForOfferer && !wasHeadlineOfferPreviouslyClosed

  const [isHeadlineOfferBannerOpen, setIsHeadlineOfferBannerOpen] = useState(
    initialIsHeadlineOfferBannerOpen
  )

  useEffect(() => {
    setIsHeadlineOfferBannerOpen(initialIsHeadlineOfferBannerOpen)
  }, [initialIsHeadlineOfferBannerOpen])

  const { data: rawHeadlineOffer, error } = useSWR(
    selectedOffererId && isHeadlineOfferAllowedForOfferer
      ? [GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId]
      : null,
    ([, offererId]) => api.getOffererHeadlineOffer(offererId),
    {
      onError: (error) => {
        // 404 is expected when there is no headline offer.
        if (error.status !== 404) {
          throw error
        }
      },
      onErrorRetry: (error) => {
        // By default, SWR retries on error. We don't want to retry on 404,
        // since it's expected when there is no headline offer.
        if (error.status === 404) {
          return
        }
      },
    }
  )

  // Sometimes rawHeadlineOffer still contains cached data while the offer is no longer an headline offer,
  // by different means that didn't trigger a mutation (e.g. the offer has 0 stock, is deactivated).
  const headlineOffer = error ? null : (rawHeadlineOffer ?? null)

  const closeHeadlineOfferBanner = () => {
    setIsHeadlineOfferBannerOpen(false)
    if (storageAvailable('localStorage')) {
      localStorage.setItem(
        LOCAL_STORAGE_HEADLINE_OFFER_BANNER_CLOSED_KEY,
        'true'
      )
    }
  }

  const upsertHeadlineOffer = async ({
    offerId,
    context,
  }: UpsertHeadlineOfferParams) => {
    try {
      await mutate(
        [GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId],
        api.upsertHeadlineOffer({ offerId }),
        { revalidate: true, throwOnError: true }
      )

      notify.success('Votre offre a été mise à la une !')
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
        await mutate(
          [GET_OFFERER_HEADLINE_OFFER_QUERY_KEY, selectedOffererId],
          api.deleteHeadlineOffer({ offererId: selectedOffererId }),
          {
            populateCache: () => null,
            revalidate: false,
            throwOnError: true,
          }
        )

        notify.success('Votre offre n’est plus à la une')
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
    <HeadlineOfferContext.Provider
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
    </HeadlineOfferContext.Provider>
  )
}
