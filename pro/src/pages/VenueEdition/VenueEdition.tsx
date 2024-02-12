import { Navigate, useParams } from 'react-router-dom'

import { OfferStatus } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { setInitialFormValues } from 'components/VenueForm'
import useGetOfferer from 'core/Offerers/getOffererAdapter/useGetOfferer'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useGetVenue } from 'core/Venue/adapters/getVenueAdapter'
import { useGetVenueLabels } from 'core/Venue/adapters/getVenueLabelsAdapter'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { useAdapter } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import fullPlusIcon from 'icons/full-more.svg'
import {
  getFilteredOffersAdapter,
  Payload,
} from 'pages/Offers/adapters/getFilteredOffersAdapter'
import { VenueEditionFormScreen } from 'screens/VenueForm/VenueEditionFormScreen'
import { Title } from 'ui-kit'
import Button from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import useGetProviders from '../../core/Venue/adapters/getProviderAdapter/useGetProvider'
import useGetVenueProviders from '../../core/Venue/adapters/getVenueProviderAdapter/useGetVenueProvider'

import { offerHasBookingQuantity } from './utils'
import styles from './VenueEdition.module.scss'

export const VenueEdition = (): JSX.Element | null => {
  const isNewBankDetailsEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const isNewSideBarNavigation = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')
  const homePath = '/accueil'
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const notify = useNotification()
  const {
    isLoading: isLoadingVenue,
    error: errorVenue,
    data: venue,
  } = useGetVenue(Number(venueId))
  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()
  const {
    isLoading: isLoadingVenueLabels,
    error: errorVenueLabels,
    data: venueLabels,
  } = useGetVenueLabels()
  const {
    isLoading: isLoadingOfferer,
    error: errorOfferer,
    data: offerer,
  } = useGetOfferer(offererId)
  const {
    isLoading: isLoadingProviders,
    error: errorProviders,
    data: providers,
  } = useGetProviders(Number(venueId))
  const {
    isLoading: isLoadingVenueProviders,
    error: errorVenueProviders,
    data: venueProviders,
  } = useGetVenueProviders(Number(venueId))

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    status: OfferStatus.ACTIVE,
    venueId: venue?.id.toString() ?? '',
  }

  const { isLoading: isLoadingVenueOffers, data: venueOffers } = useAdapter<
    Payload,
    Payload
  >(() => getFilteredOffersAdapter(apiFilters))

  const hasBookingQuantity = offerHasBookingQuantity(venueOffers?.offers)

  if (
    errorOfferer ||
    errorVenue ||
    errorVenueTypes ||
    errorVenueLabels ||
    errorVenueProviders ||
    errorProviders
  ) {
    const loadingError = [
      errorOfferer,
      errorVenue,
      errorVenueTypes,
      errorVenueLabels,
    ].find((error) => error !== undefined)
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
      return <Navigate to={homePath} />
    }
    /* istanbul ignore next: Never */
    return null
  }

  const {
    id: initialId,
    isVirtual: initialIsVirtual,
    publicName: publicName,
    name: initialName,
  } = venue || {}

  return (
    <AppLayout>
      {isLoadingVenue ||
      isLoadingVenueTypes ||
      isLoadingVenueLabels ||
      isLoadingProviders ||
      isLoadingVenueProviders ||
      isLoadingOfferer ||
      isLoadingVenueOffers ? (
        <Spinner />
      ) : (
        <div>
          <div className={styles['venue-form-heading']}>
            <div className={styles['title-page']}>
              <Title level={1}>Lieu</Title>

              {!isNewSideBarNavigation && (
                <a
                  href={`/offre/creation?lieu=${initialId}&structure=${offerer.id}`}
                >
                  <Button variant={ButtonVariant.PRIMARY} icon={fullPlusIcon}>
                    <span>Créer une offre</span>
                  </Button>
                </a>
              )}
            </div>
            <Title level={2} className={styles['venue-name']}>
              {
                /* istanbul ignore next: DEBT, TO FIX */ initialIsVirtual
                  ? `${offerer.name} (Offre numérique)`
                  : publicName || initialName
              }
            </Title>
            {
              /* istanbul ignore next: DEBT, TO FIX */
              !isNewBankDetailsEnabled && (
                <>
                  {/* For the screen reader to spell-out the id, we add a
                visually hidden span with a space between each character.
                The other span will be hidden from the screen reader. */}
                  <span className={styles['identifier-hidden']}>
                    Identifiant du lieu : {venue.dmsToken.split('').join(' ')}
                  </span>
                  <span aria-hidden={true}>
                    Identifiant du lieu : {venue.dmsToken}
                  </span>
                </>
              )
            }
          </div>

          <VenueEditionFormScreen
            initialValues={setInitialFormValues(venue)}
            offerer={offerer}
            venueTypes={venueTypes}
            venueLabels={venueLabels}
            providers={providers}
            venue={venue}
            venueProviders={venueProviders}
            hasBookingQuantity={venue?.id ? hasBookingQuantity : false}
          />
        </div>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
