import { useState } from 'react'
import { useNavigate } from 'react-router'

import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFocusOnMounted } from '@/commons/hooks/useFocusOnMounted'
import { setSelectedVenueById } from '@/commons/store/user/dispatchers/setSelectedVenueById'
import { ensureVenues } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Footer } from '@/components/Footer/Footer'
import fullMoreIcon from '@/icons/full-more.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './Hub.module.scss'

export const Hub = () => {
  const dispatch = useAppDispatch()
  const venues = useAppSelector(ensureVenues)
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = useState(false)

  const setSelectedVenueByIdAndRedirect = async (
    nextSelectedVenueId: number
  ) => {
    setIsLoading(true)
    await dispatch(setSelectedVenueById(nextSelectedVenueId)).unwrap()

    navigate('/accueil')
  }

  useFocusOnMounted('#content', isLoading)

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
      <div className={styles['venue-list']}>
        {venues.map((venue) => (
          <div key={venue.id}>
            <button
              aria-describedby={
                venue.location ? `venue-${venue.id}-location` : undefined
              }
              className={styles['venue-item-button']}
              onClick={() => setSelectedVenueByIdAndRedirect(venue.id)}
              type="button"
            >
              <span
                className={styles['venue-item-name']}
                id={`venue-${venue.id}`}
              >
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

      <div className={styles['venue-actions']}>
        <ButtonLink
          icon={fullMoreIcon}
          to="/inscription/structure/recherche"
          variant={ButtonVariant.SECONDARY}
        >
          Ajouter une structure
        </ButtonLink>
      </div>

      <Footer layout={'basic'} />
    </FunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Hub
