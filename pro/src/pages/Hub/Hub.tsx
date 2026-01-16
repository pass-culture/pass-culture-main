import { type ChangeEvent, useRef, useState } from 'react'
import { useNavigate } from 'react-router'

import type { VenueListItemResponseModel } from '@/apiClient/v1'
import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFocusOnMounted } from '@/commons/hooks/useFocusOnMounted'
import { setSelectedVenueById } from '@/commons/store/user/dispatchers/setSelectedVenueById'
import { ensureVenues } from '@/commons/store/user/selectors'
import { normalizeStrForSearch } from '@/commons/utils/normalizeStrForSearch'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Footer } from '@/components/Footer/Footer'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'
import fullMoreIcon from '@/icons/full-more.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './Hub.module.scss'

export const Hub = () => {
  const venuesWithNormalizedNameRef = useRef<
    [normalizedName: string, venue: VenueListItemResponseModel][]
  >([])

  const dispatch = useAppDispatch()
  const venues = useAppSelector(ensureVenues)
  const navigate = useNavigate()

  const [filteredVenues, setFilteredVenues] = useState(venues)
  const [isLoading, setIsLoading] = useState(false)
  const [query, setQuery] = useState('')

  const filterVenues = (event: ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value

    setQuery(query)

    const normalizedQuery = normalizeStrForSearch(event.target.value)
    if (!normalizedQuery) {
      setFilteredVenues(venues)

      return
    }

    if (venuesWithNormalizedNameRef.current.length === 0) {
      venuesWithNormalizedNameRef.current = venues.map((venue) => [
        normalizeStrForSearch(venue.publicName),
        venue,
      ])
    }

    setFilteredVenues(
      venuesWithNormalizedNameRef.current
        .filter(([normalizedName]) => normalizedName.includes(normalizedQuery))
        .map(([, venue]) => venue)
    )
  }

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
      tabIndex={-1}
    >
      {venues.length > 4 && (
        <SearchInput
          label="Rechercher une structure"
          onChange={filterVenues}
          value={query}
          name="searchQuery"
        />
      )}

      {/* Hidden helper text for screen readers */}
      {
        // biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`.
        <div
          className={styles['sr-only']}
          role="status"
          aria-atomic="true"
          aria-live="polite"
        >
          {!!query &&
            `${filteredVenues.length} ${pluralizeFr(filteredVenues.length, 'structure trouvée', 'structures trouvées')}.`}
        </div>
      }
      {filteredVenues.length === 0 && (
        <div className={styles['no-results']}>
          Aucune structure ne correspond à votre recherche "{query}".
        </div>
      )}
      <div className={styles['venue-list']}>
        {filteredVenues.map((venue) => (
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
                id={`venue-${venue.id}-name`}
              >
                {venue.publicName}
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
