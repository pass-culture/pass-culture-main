import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { SelectOption } from 'custom_types/form'
import { ReactComponent as StatsIconGrey } from 'icons/ico-stats-grey.svg'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import Titles from 'ui-kit/Titles/Titles'
import { sortByLabel } from 'utils/strings'

import OffererStatsNoResult from '../../components/OffererStatsNoResult'

import styles from './OffererStatsScreen.module.scss'

interface OffererStatsScreenProps {
  offererOptions: SelectOption[]
}

const OffererStatsScreen = ({ offererOptions }: OffererStatsScreenProps) => {
  const [iframeUrl, setIframeUrl] = useState('')
  const [selectedOffererId, setSelectedOffererId] = useState(
    offererOptions[0].value
  )
  const [selectedVenueId, setSelectedVenueId] = useState('')
  const [venueOptions, setVenueOptions] = useState<SelectOption[]>([])
  const ALL_VENUES_OPTION = {
    value: 'all',
    label: 'Tous les lieux',
  }

  const handleChangeOfferer = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOffererId = event.target.value
    setSelectedOffererId(selectedOffererId)
  }
  const handleChangeVenue = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedVenueId = event.target.value
    setSelectedVenueId(selectedVenueId)
  }

  useEffect(() => {
    api.getOfferer(Number(selectedOffererId)).then(offerer => {
      if (offerer.managedVenues) {
        const sortedVenueOptions = sortByLabel(
          offerer.managedVenues
            .filter(
              venue =>
                offerer.hasDigitalVenueAtLeastOneOffer || !venue.isVirtual
            )
            .map(venue => ({
              value: venue.nonHumanizedId.toString(),
              label: venue.publicName || venue.name,
            }))
        )
        setVenueOptions([ALL_VENUES_OPTION, ...sortedVenueOptions])

        setSelectedVenueId(sortedVenueOptions[0].value.toString())
      } else {
        setVenueOptions([])
      }
    })
  }, [selectedOffererId])

  useEffect(() => {
    const updateDashboardUrl = async (venueId: string) => {
      let response = null
      if (!venueId) {
        setIframeUrl('')
        return
      }
      if (venueId == 'all') {
        response = await api.getOffererStatsDashboardUrl(
          Number(selectedOffererId)
        )
      } else {
        response = await api.getVenueStatsDashboardUrl(Number(selectedVenueId))
      }
      setIframeUrl(response.dashboardUrl)
    }
    updateDashboardUrl(selectedVenueId)
  }, [selectedVenueId, selectedOffererId])

  return (
    <div className={styles['offerer-stats']}>
      <Titles title="Statistiques" />
      <p className={styles['offerer-stats-description']}>
        Vos statistiques sont calculées et mises à jour quotidiennement dans la
        nuit.
      </p>

      <FieldLayout label="Structure" name="offererId">
        <SelectInput
          onChange={handleChangeOfferer}
          name="offererId"
          options={offererOptions}
          value={String(selectedOffererId)}
          disabled={offererOptions.length <= 1}
        />
      </FieldLayout>

      {venueOptions.length > 0 && iframeUrl ? (
        <>
          <FieldLayout label="Lieu" name="venueId">
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
          icon={<StatsIconGrey />}
        />
      )}
    </div>
  )
}

export default OffererStatsScreen
