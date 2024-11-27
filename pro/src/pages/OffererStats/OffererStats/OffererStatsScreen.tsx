import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { sortByLabel } from 'commons/utils/strings'
import { OffererStatsNoResult } from 'components/OffererStatsNoResult/OffererStatsNoResult'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './OffererStatsScreen.module.scss'

export const OffererStatsScreen = () => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  const isOffererStatsV2Active = useActiveFeature('WIP_OFFERER_STATS_V2')
  const targetOffererId = useSelector(selectCurrentOffererId)

  const [iframeUrl, setIframeUrl] = useState('')
  const [selectedVenueId, setSelectedVenueId] = useState('all')
  const [venueOptions, setVenueOptions] = useState<SelectOption[]>([])

  if (isOffererStatsV2Active) {
    return (
      <Navigate to="/remboursements/revenus" replace={true} relative="path" />
    )
  }

  const ALL_VENUES_OPTION = {
    value: 'all',
    label: isOfferAddressEnabled ? 'Tous' : 'Tous les lieux',
  }
  const handleChangeVenue = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedVenueId = event.target.value
    setSelectedVenueId(selectedVenueId)
  }

  useEffect(() => {
    async function loadData() {
      const offerer = await api.getOfferer(Number(targetOffererId))
      if (offerer.managedVenues && offerer.managedVenues.length > 0) {
        const sortedVenueOptions = sortByLabel(
          offerer.managedVenues
            .filter(
              (venue) =>
                offerer.hasDigitalVenueAtLeastOneOffer || !venue.isVirtual
            )
            .map((venue) => ({
              value: venue.id.toString(),
              label: venue.publicName || venue.name,
            }))
        )
        setVenueOptions([ALL_VENUES_OPTION, ...sortedVenueOptions])
      } else {
        setVenueOptions([])
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadData()
  }, [targetOffererId])

  useEffect(() => {
    const updateDashboardUrl = async (venueId: string) => {
      let response = null
      if (!venueId) {
        setIframeUrl('')
        return
      }
      if (venueId === 'all') {
        response = await api.getOffererStatsDashboardUrl(
          Number(targetOffererId)
        )
      } else {
        response = await api.getVenueStatsDashboardUrl(Number(selectedVenueId))
      }
      setIframeUrl(response.dashboardUrl)
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    updateDashboardUrl(selectedVenueId)
  }, [selectedVenueId, targetOffererId])

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
