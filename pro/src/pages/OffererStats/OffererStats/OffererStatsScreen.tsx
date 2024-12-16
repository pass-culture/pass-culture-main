import React, { useState } from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GET_DEPRECATED_STATISTIC_DASHBOARD,
  GET_OFFERER_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { sortByLabel } from 'commons/utils/strings'
import { OffererStatsNoResult } from 'components/OffererStatsNoResult/OffererStatsNoResult'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './OffererStatsScreen.module.scss'

export const OffererStatsScreen = () => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  const isOffererStatsV2Active = useActiveFeature('WIP_OFFERER_STATS_V2')
  const targetOffererId = useSelector(selectCurrentOffererId)

  const [selectedVenueId, setSelectedVenueId] = useState('all')

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, Number(targetOffererId)],
    ([, offererId]) => api.getOfferer(offererId)
  )

  const getOffererStatsDashboardUrlQuery = useSWR(
    selectedVenueId
      ? [GET_DEPRECATED_STATISTIC_DASHBOARD, selectedVenueId]
      : null,
    ([, venueId]) => {
      if (venueId === 'all') {
        return api.getOffererStatsDashboardUrl(Number(targetOffererId))
      }
      return api.getVenueStatsDashboardUrl(Number(selectedVenueId))
    }
  )

  if (offererQuery.isLoading || !offererQuery.data) {
    return <Spinner />
  }

  if (isOffererStatsV2Active) {
    return (
      <Navigate to="/remboursements/revenus" replace={true} relative="path" />
    )
  }

  const iframeUrl = getOffererStatsDashboardUrlQuery.data?.dashboardUrl ?? ''

  let venueOptions: SelectOption[] = []
  const ALL_VENUES_OPTION = {
    value: 'all',
    label: isOfferAddressEnabled ? 'Tous' : 'Tous les lieux',
  }
  const offerer = offererQuery.data
  if (offerer.managedVenues && offerer.managedVenues.length > 0) {
    const sortedVenueOptions = sortByLabel(
      offerer.managedVenues
        .filter(
          (venue) => offerer.hasDigitalVenueAtLeastOneOffer || !venue.isVirtual
        )
        .map((venue) => ({
          value: venue.id.toString(),
          label: venue.publicName || venue.name,
        }))
    )
    venueOptions = [ALL_VENUES_OPTION, ...sortedVenueOptions]
  } else {
    venueOptions = []
  }

  const handleChangeVenue = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedVenueId = event.target.value
    setSelectedVenueId(selectedVenueId)
  }

  return (
    <div className={styles['offerer-stats']}>
      <h1 className={styles['title']}>Statistiques</h1>
      <p className={styles['offerer-stats-description']}>
        Vos statistiques sont calculées et mises à jour quotidiennement dans la
        nuit.
      </p>

      {venueOptions.length > 0 && iframeUrl ? (
        <>
          <FieldLayout
            label={isOfferAddressEnabled ? 'Partenaire culturel' : 'Lieu'}
            name="venueId"
            isOptional
          >
            <SelectInput
              onChange={handleChangeVenue}
              name="venueId"
              options={venueOptions}
              value={selectedVenueId}
              disabled={venueOptions.length <= 1}
            />
          </FieldLayout>

          <div className={styles['iframe-container']}>
            <iframe
              title="Tableau des statistiques"
              className={styles['dashboard-iframe']}
              src={iframeUrl}
            />
          </div>
        </>
      ) : (
        <OffererStatsNoResult
          extraClassName={styles['no-result-section']}
          title={'Aucune donnée à afficher'}
          subtitle={
            'Vos données statistiques s’afficheront dès la première réservation.'
          }
        />
      )}
    </div>
  )
}
