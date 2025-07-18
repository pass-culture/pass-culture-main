import { useEffect, useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { generatePath, useLocation, useNavigate, useParams } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_VENUE_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { SelectOption } from 'commons/custom_types/form'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { setSelectedPartnerPageId } from 'commons/store/nav/reducer'
import { selectCurrentOfferer } from 'commons/store/offerer/selectors'
import { getVenuePagePathToNavigateTo } from 'commons/utils/getVenuePagePathToNavigateTo'
import { setSavedPartnerPageVenueId } from 'commons/utils/savedPartnerPageVenueId'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CollectiveDataEdition } from 'pages/Offerers/Offerer/VenueV1/VenueEdition/CollectiveDataEdition/CollectiveDataEdition'
import { SelectInput } from 'ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { NavLinkItem, NavLinkItems } from 'ui-kit/NavLinkItems/NavLinkItems'
import { Spinner } from 'ui-kit/Spinner/Spinner'

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
  const currentOfferer = useSelector(selectCurrentOfferer)
  const selectedOffererId = currentOfferer?.id ?? null

  const venueQuery = useSWR(
    [GET_VENUE_QUERY_KEY, venueId],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )
  const venue = venueQuery.data

  const { data: offerer, isLoading: isOffererLoading } = useOfferer(offererId)

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const context = location.pathname.includes('collectif')
    ? 'collective'
    : location.pathname.includes('page-partenaire')
      ? 'partnerPage'
      : 'address'

  const filteredVenues = useMemo(() => {
    if (context === 'partnerPage') {
      return (
        offerer?.managedVenues?.filter((venue) => venue.hasPartnerPage) ?? []
      )
    }

    return offerer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []
  }, [context, offerer?.managedVenues])

  const venuesOptions: SelectOption[] = filteredVenues.map((venue) => ({
    label: venue.publicName || venue.name,
    value: venue.id.toString(),
  }))

  useEffect(() => {
    if (selectedOffererId?.toString() !== offererId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate('/accueil')
    }
  }, [selectedOffererId, offererId])

  useEffect(() => {
    if (context === 'partnerPage' && offerer) {
      // Selected venue is no longer in the list of hasPartnerPage venues.
      // On browser tab return, data is revalidated, and offerer.managedVenues
      // is updated - but venueId is not. In SelectInput, there is a
      // natural fallback to the first element of the list - but the rest
      // of the page still needs to be updated, just like the side nav link.
      const selectedVenue = filteredVenues.find(
        (venue) => venue.id === Number(venueId)
      )

      if (!selectedVenue) {
        if (filteredVenues.length > 0) {
          const fallbackVenueId = filteredVenues[0]?.id.toString()

          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate(getVenuePagePathToNavigateTo(offerer.id, fallbackVenueId))
          dispatch(setSelectedPartnerPageId(fallbackVenueId))
        } else {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          navigate('/accueil')
        }
      }
    }
  }, [context, venueId, filteredVenues, offerer, navigate, dispatch])

  if (
    venueQuery.isLoading ||
    venueTypesQuery.isLoading ||
    isOffererLoading ||
    !venue ||
    !offerer ||
    !venueTypes
  ) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  const tabs: NavLinkItem[] = [
    {
      key: 'individual',
      label: 'Pour le grand public',
      url: generatePath('/structures/:offererId/lieux/:venueId', {
        offererId: String(venue.managingOfferer.id),
        venueId: String(venue.id),
      }),
    },
    {
      key: 'collective',
      label: 'Pour les enseignants',
      url: generatePath('/structures/:offererId/lieux/:venueId/collectif', {
        offererId: String(venue.managingOfferer.id),
        venueId: String(venue.id),
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
    <Layout mainHeading={titleText}>
      <div>
        <FormLayout>
          {context !== 'address' && venuesOptions.length > 1 && (
            <>
              <FormLayout.Row>
                <FieldLayout
                  label={`Sélectionnez votre page ${context === 'collective' ? 'dans ADAGE' : 'partenaire'}`}
                  name="venues"
                  isOptional
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
        <VenueEditionHeader
          venue={venue}
          offerer={offerer}
          venueTypes={venueTypes}
          context={context}
          key={venueId}
        />

        {!venue.isPermanent && (
          <NavLinkItems
            links={tabs}
            navLabel={`Sous menu - ${titleText}`}
            selectedKey={context === 'collective' ? 'collective' : 'individual'}
            className={styles['tabs']}
          />
        )}

        {context === 'collective' ? (
          <CollectiveDataEdition venue={venue} />
        ) : (
          <VenueEditionFormScreen venue={venue} />
        )}
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueEdition
