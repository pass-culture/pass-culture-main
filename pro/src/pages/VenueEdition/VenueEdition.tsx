import { generatePath, useLocation, useNavigate, useParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { setSelectedPartnerPageId } from '@/commons/store/nav/reducer'
import {
  ensureSelectedVenue,
  ensureVenues,
} from '@/commons/store/user/selectors'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { setSavedPartnerPageVenueId } from '@/commons/utils/savedPartnerPageVenueId'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { CollectiveDataEdition } from '@/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { formatAndOrderVenues } from '@/repository/venuesService'
import { Select } from '@/ui-kit/form/Select/Select'
import {
  type NavLinkItem,
  NavLinkItems,
} from '@/ui-kit/NavLinkItems/NavLinkItems'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { VenueEditionFormScreen } from './components/VenueEditionFormScreen'
import { VenueEditionHeader } from './components/VenueEditionHeader'
import styles from './VenueEdition.module.scss'

export const VenueEdition = (): JSX.Element | null => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  const { venueId: selectedVenueIdFromQueryParams } = useParams<{
    offererId: string
    venueId: string
  }>()
  const selectedVenueFromStore = useAppSelector(ensureSelectedVenue)
  const selectedVenueId = withSwitchVenueFeature
    ? selectedVenueFromStore.id
    : selectedVenueIdFromQueryParams
  const venues = useAppSelector(ensureVenues)

  const venueQuery = useSWR(
    withSwitchVenueFeature ? null : [GET_VENUE_QUERY_KEY, selectedVenueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = withSwitchVenueFeature
    ? selectedVenueFromStore
    : venueQuery.data

  const context = location.pathname.includes('collectif')
    ? 'collective'
    : location.pathname.includes('page-partenaire')
      ? 'partnerPage'
      : 'address'

  const venuesOptions: SelectOption[] = formatAndOrderVenues(
    venues.filter((venue) => venue.hasCreatedOffer && venue.isPermanent) ?? []
  ).map((venue) => ({
    value: String(venue.value),
    label: venue.label,
  }))

  const isNotReady = venueQuery.isLoading || !venue

  const tabs: NavLinkItem[] = [
    {
      key: 'individual',
      label: 'Pour le grand public',
      url: generatePath('/structures/:offererId/lieux/:venueId', {
        offererId: String(venue?.managingOfferer.id),
        venueId: String(venue?.id),
      }),
    },
    {
      key: 'collective',
      label: 'Pour les enseignants',
      url: generatePath('/structures/:offererId/lieux/:venueId/collectif', {
        offererId: String(venue?.managingOfferer.id),
        venueId: String(venue?.id),
      }),
    },
  ]

  const titleText =
    context === 'collective'
      ? 'Page dans ADAGE'
      : context === 'partnerPage'
        ? 'Page sur l’application'
        : 'Page adresse'

  return (
    <BasicLayout mainHeading={titleText}>
      {isNotReady ? (
        <Spinner />
      ) : (
        <div>
          {!withSwitchVenueFeature && (
            <FormLayout>
              {context !== 'address' && venuesOptions.length > 1 && (
                <>
                  <FormLayout.Row>
                    <Select
                      label={`Sélectionnez votre page ${context === 'collective' ? 'dans ADAGE' : 'partenaire'}`}
                      name="venues"
                      className={styles['select-page-partenaire']}
                      options={venuesOptions}
                      value={selectedVenueId?.toString() ?? ''}
                      onChange={(e) => {
                        const venueId = e.target.value

                        if (context === 'partnerPage') {
                          setSavedPartnerPageVenueId(
                            'partnerPage',
                            venue.managingOfferer.id,
                            venueId
                          )

                          dispatch(setSelectedPartnerPageId(venueId))
                        }

                        const path = getVenuePagePathToNavigateTo(
                          venue.managingOfferer.id,
                          venueId
                        )
                        navigate(path)
                      }}
                    />
                  </FormLayout.Row>
                  <hr className={styles['separator']} />
                </>
              )}
            </FormLayout>
          )}
          <VenueEditionHeader venue={venue} context={context} key={venue.id} />

          {!venue.isPermanent && (
            <NavLinkItems
              links={tabs}
              navLabel={`Sous menu - ${titleText}`}
              selectedKey={
                context === 'collective' ? 'collective' : 'individual'
              }
              className={styles['tabs']}
            />
          )}

          {context === 'collective' ? (
            <CollectiveDataEdition venue={venue} />
          ) : (
            <VenueEditionFormScreen venue={venue} />
          )}
        </div>
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
