import React, { createContext, useContext, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { useHomePath, useNavigate } from 'hooks'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

export interface IAppContextLoading {
  offererNames: []
  venues: []
  selectedVenue: null
  reload: null
  selectedOffererId: null
  setSelectedOffererId: null
  selectedVenueId: null
  setSelectedVenueId: null
  shouldSelectOfferer: boolean
  isLoading: true
}

export interface IAppContext {
  offererNames: GetOffererNameResponseModel[]
  venues: VenueListItemResponseModel[]
  selectedVenue: VenueListItemResponseModel | null
  reload: () => void
  selectedOffererId: string | null
  setSelectedOffererId: (offererId: string) => void
  selectedVenueId: string | null
  setSelectedVenueId: (venueId: string) => void
  shouldSelectOfferer: boolean
  isLoading: false
}

const NB_DISPLAYED_OFFERER = 5

export const AppContext = createContext<IAppContext | IAppContextLoading>({
  offererNames: [],
  venues: [],
  reload: null,
  selectedVenue: null,
  selectedOffererId: null,
  selectedVenueId: null,
  setSelectedOffererId: null,
  setSelectedVenueId: null,
  shouldSelectOfferer: false,
  isLoading: true,
})

export const useAppContext = () => {
  return useContext(AppContext)
}

interface IAppContextProviderProps {
  children: React.ReactNode
}

export function AppContextProvider({ children }: IAppContextProviderProps) {
  const homePath = useHomePath()
  const notify = useNotification()
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [shouldSelectOfferer, setShouldSelectOfferer] = useState<boolean>(false)
  const [offererNames, setOffererNames] = useState<
    GetOffererNameResponseModel[]
  >([])
  const [venues, setVenues] = useState<VenueListItemResponseModel[]>([])
  const [selectedVenueId, setSelectedVenueId] = useState<string | null>(null)
  const [selectedVenue, setSelectedVenue] =
    useState<VenueListItemResponseModel | null>(null)
  const [selectedOffererId, setSelectedOffererId] = useState<string | null>(
    null
  )

  const loadOffererNames = async () => {
    const response = await api.listOfferersNames(
      true, // validated?: boolean | null,
      true, // validatedForUser?: boolean | null,
      null // offererId?: string | null,
    )
    const offererNamesSorted = response.offerersNames.sort((a, b) =>
      a.name.localeCompare(b.name, 'fr')
    )
    setOffererNames(offererNamesSorted)
    setSelectedOffererId(offererNamesSorted[0].id)
    return offererNamesSorted
  }

  const loadVenues = async (offererId?: string) => {
    const response = await api.getVenues(
      null, // validatedForUser?: boolean | null,
      null, // validated?: boolean | null,
      null, // activeOfferersOnly?: boolean | null,
      offererId || null // offererId?: string | null,
    )
    const venuesSorted = response.venues.sort((a, b) =>
      a.name.localeCompare(b.name, 'fr')
    )
    setVenues(venuesSorted)
    setSelectedVenueId(venuesSorted[0].id)
    setSelectedVenue(venuesSorted[0])
    return venuesSorted
  }

  const loadData = async () => {
    try {
      const offererNamesLoaded = await loadOffererNames()
      setShouldSelectOfferer(offererNamesLoaded.length > NB_DISPLAYED_OFFERER)
      if (offererNamesLoaded.length <= NB_DISPLAYED_OFFERER) {
        await loadVenues()
      } else {
        await handleSetSelectedOffererId(offererNamesLoaded[0].id)
      }
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
      navigate(homePath)
    }
  }

  const handleSetSelectedVenueId = (venueId: string) => {
    const venue = venues.find(v => v.id === venueId)
    if (venue === undefined) {
      notify.error(GET_DATA_ERROR_MESSAGE)
      navigate(homePath)
      return
    }
    setSelectedVenueId(venueId)
    setSelectedVenue(venue)
  }

  const handleSetSelectedOffererId = async (offererId: string) => {
    const offererName = offererNames.find(o => o.id === offererId)
    if (offererName === undefined) {
      notify.error(GET_DATA_ERROR_MESSAGE)
      navigate(homePath)
      return
    }
    setSelectedOffererId(offererId)
    if (offererNames.length > NB_DISPLAYED_OFFERER) {
      await loadVenues(offererId)
    }
  }

  useEffect(() => {
    ;(async () => {
      await loadData()
      setIsLoading(false)
    })()
  }, [])

  if (isLoading === true) {
    return <Spinner />
  }

  return (
    <AppContext.Provider
      value={
        {
          offererNames,
          venues,
          reload: loadData,
          selectedVenue,
          selectedOffererId,
          selectedVenueId,
          setSelectedOffererId: handleSetSelectedOffererId,
          setSelectedVenueId: handleSetSelectedVenueId,
          shouldSelectOfferer,
          isLoading: false,
        } as IAppContext
      }
    >
      {children}
    </AppContext.Provider>
  )
}
