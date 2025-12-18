import { useState } from 'react'

import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import { RouteId } from '@/app/AppRouter/constants'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFocusOnMounted } from '@/commons/hooks/useFocusOnMounted'
import { useNavigateByRouteId } from '@/commons/hooks/useNavigateByRouteId'
import { setSelectedVenueById } from '@/commons/store/user/dispatchers/setSelectedVenueById'
import { ensureVenues } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './Hub.module.scss'

export const Hub = () => {
  const dispatch = useAppDispatch()
  const venues = useAppSelector(ensureVenues)
  const navigateByRouteId = useNavigateByRouteId()

  const [isLoading, setIsLoading] = useState(false)

  const setSelectedVenueByIdAndRedirect = async (
    nextSelectedVenueId: number
  ) => {
    setIsLoading(true)

    const nextUserAccess = await dispatch(
      setSelectedVenueById(nextSelectedVenueId)
    ).unwrap()
    if (nextUserAccess === 'full') {
      navigateByRouteId(RouteId.Homepage)
    }
  }

  useFocusOnMounted('#content')

  if (isLoading) {
    return (
      <div aria-busy="true" className={styles['spinner-container']}>
        <Spinner message="Chargement de la structure en cours…" />
      </div>
    )
  }

  return (
    <FunnelLayout
      mainHeading="À quelle structure souhaitez-vous accéder ?"
      withFlexContent
    >
      <div className={styles['venue-buttons-box']}>
        {venues.map((venue) => (
          <div key={venue.id}>
            <button
              aria-describedby={
                venue.location ? `venue-${venue.id}-location` : undefined
              }
              className={styles['venue-button']}
              onClick={() => setSelectedVenueByIdAndRedirect(venue.id)}
              type="button"
            >
              <span className={styles['venue-name']} id={`venue-${venue.id}`}>
                {venue.name}
              </span>
              {venue.location && (
                <span
                  className={styles['venue-location']}
                  id={`venue-${venue.id}-location`}
                >
                  {withVenueHelpers(venue).fullAddressAsString}
                </span>
              )}
            </button>
          </div>
        ))}
      </div>
    </FunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Hub
