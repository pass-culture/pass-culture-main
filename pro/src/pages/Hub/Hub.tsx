import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureCurrentUser, ensureVenues } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'

import styles from './Hub.module.scss'

export const Hub = () => {
  const currentUser = useAppSelector(ensureCurrentUser)
  const venues = useAppSelector(ensureVenues)

  return (
    <OnboardingLayout
      mainHeading={`Bienvenue ${currentUser.firstName},`}
      isStickyActionBarInChild
    >
      <div style={{ width: '100%' }}>
        <p>À quelle structure souhaitez-vous accéder ?</p>
        <div className={styles.venue_buttons_box}>
          {venues.map((venue) => (
            <div key={venue.id}>
              <button className={styles.venue_button} type="button">
                <p>{venue.name}</p>
                {venue.address && (
                  <p>{withVenueHelpers(venue).fullAddressAsString}</p>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Hub
