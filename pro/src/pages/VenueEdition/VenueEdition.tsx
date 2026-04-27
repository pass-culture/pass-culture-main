import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { CollectiveDataEdition } from '@/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VenueEditionFormScreen } from './components/VenueEditionFormScreen'
import { VenueEditionHeader } from './components/VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const location = useLocation()
  const hasSeenVolunteeringSection =
    localStorageManager.getItem(
      LOCAL_STORAGE_KEY.HAS_SEEN_VOLUNTEERING_SECTION
    ) === 'true'
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const selectedVenueId = selectedPartnerVenue.id

  const { syncVenue } = useSyncVenueCache()
  useEffect(() => {
    if (selectedVenueId) {
      syncVenue(Number(selectedVenueId))
    }
  }, [selectedVenueId])

  const context = location.pathname.includes('collectif')
    ? 'collective'
    : 'partnerPage'

  useEffect(() => {
    if (context === 'partnerPage' && !hasSeenVolunteeringSection) {
      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.HAS_SEEN_VOLUNTEERING_SECTION,
        'true'
      )
    }
  }, [context, hasSeenVolunteeringSection])

  const titleText =
    context === 'collective' ? 'Page dans ADAGE' : 'Page sur l’application'
  return (
    <BasicLayout mainHeading={titleText}>
      {!selectedPartnerVenue ? (
        <Spinner />
      ) : (
        <div>
          <VenueEditionHeader
            venue={selectedPartnerVenue}
            context={context}
            key={selectedPartnerVenue.id}
          />

          {context === 'collective' ? (
            <CollectiveDataEdition venue={selectedPartnerVenue} />
          ) : (
            <VenueEditionFormScreen venue={selectedPartnerVenue} />
          )}
        </div>
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
