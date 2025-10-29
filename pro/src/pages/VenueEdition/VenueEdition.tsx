import { useDispatch, useSelector } from 'react-redux'
import { generatePath, useLocation, useNavigate, useParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  GET_VENUE_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import type { SelectOption } from '@/commons/custom_types/form'
import { setSelectedPartnerPageId } from '@/commons/store/nav/reducer'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { setSavedPartnerPageVenueId } from '@/commons/utils/savedPartnerPageVenueId'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { CollectiveDataEdition } from '@/pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { formatAndOrderVenues } from '@/repository/venuesService'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'
import {
  type NavLinkItem,
  NavLinkItems,
} from '@/ui-kit/NavLinkItems/NavLinkItems'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './VenueEdition.module.scss'
import { VenueEditionFormScreen } from './VenueEditionFormScreen'
import { VenueEditionHeader } from './VenueEditionHeader'

export const VenueEdition = (): JSX.Element | null => {
  const { offererId, venueId } = useParams<{
    offererId: string
    venueId: string
  }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const venuesQuery = useSWR([GET_VENUES_QUERY_KEY, offererId], () =>
    api.getVenues(true, true, selectedOffererId)
  )

  const context = location.pathname.includes('collectif')
    ? 'collective'
    : location.pathname.includes('page-partenaire')
      ? 'partnerPage'
      : 'address'

  const venuesOptions: SelectOption[] = formatAndOrderVenues(
    venuesQuery?.data?.venues?.filter(
      (venue) => venue.hasCreatedOffer && venue.isPermanent
    ) ?? []
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
          <FormLayout>
            {context !== 'address' && venuesOptions.length > 1 && (
              <>
                <FormLayout.Row>
                  <FieldLayout
                    label={`Sélectionnez votre page ${context === 'collective' ? 'dans ADAGE' : 'partenaire'}`}
                    name="venues"
                    required={false}
                    className={styles['select-page-partenaire']}
                  >
                    <SelectInput
                      name="venues"
                      options={venuesOptions}
                      value={venueId ?? ''}
                      onChange={(e) => {
                        const venueId = e.target.value

                        if (context === 'partnerPage') {
                          setSavedPartnerPageVenueId(
                            'partnerPage',
                            offererId,
                            venueId
                          )

                          dispatch(setSelectedPartnerPageId(venueId))
                        }

                        const path = getVenuePagePathToNavigateTo(
                          offererId as string,
                          venueId
                        )
                        // eslint-disable-next-line @typescript-eslint/no-floating-promises
                        navigate(path)
                      }}
                    />
                  </FieldLayout>
                </FormLayout.Row>
                <hr className={styles['separator']} />
              </>
            )}
          </FormLayout>
          <VenueEditionHeader venue={venue} context={context} key={venueId} />

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
