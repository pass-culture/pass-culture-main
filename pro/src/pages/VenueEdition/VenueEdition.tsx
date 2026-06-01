import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { CollectiveDataEdition } from '@/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VenueEditionFormScreen } from './components/VenueEditionFormScreen'
import { VenueEditionHeader } from './components/VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const location = useLocation()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const selectedVenueId = selectedPartnerVenue.id

  const { syncVenue } = useSyncVenueCache()
  useEffect(() => {
    if (selectedVenueId) {
      syncVenue(Number(selectedVenueId))
    }
  }, [selectedVenueId])

  const context = location.pathname.includes('page-collective')
    ? 'collective'
    : 'partnerPage'

  const titleText =
    context === 'collective' ? 'Page dans ADAGE' : 'Page sur l’application'
  return (
    <BasicLayout mainHeading={titleText}>
      {selectedPartnerVenue ? (
        <div>
          <VenueEditionHeader
            venue={selectedPartnerVenue}
            context={context}
            key={selectedPartnerVenue.id}
          />

          {context === 'collective' ? (
            <CollectiveDataEdition />
          ) : (
            <VenueEditionFormScreen venue={selectedPartnerVenue} />
          )}
        </div>
      ) : (
        <Spinner />
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
