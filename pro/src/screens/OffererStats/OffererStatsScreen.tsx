import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { Option } from 'core/Offers/types'
import { ReactComponent as StatsIconGrey } from 'icons/ico-stats-grey.svg'
import Select from 'ui-kit/form_raw/Select'
import Titles from 'ui-kit/Titles/Titles'
import { sortByDisplayName } from 'utils/strings'

import OffererStatsNoResult from '../../components/OffererStatsNoResult'

import styles from './OffererStatsScreen.module.scss'

interface IOffererStatsScreenProps {
  offererOptions: Option[]
}

const OffererStatsScreen = ({ offererOptions }: IOffererStatsScreenProps) => {
  const [iframeUrl, setIframeUrl] = useState('')
  const [selectedOffererId, setSelectedOffererId] = useState(
    offererOptions[0].id
  )
  const [selectedVenueId, setSelectedVenueId] = useState('')
  const [venueOptions, setVenueOptions] = useState<Option[]>([])
  const ALL_VENUES_OPTION = {
    id: 'all',
    displayName: 'Tous les lieux',
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
        const sortedVenueOptions = sortByDisplayName(
          offerer.managedVenues
            .filter(
              venue =>
                offerer.hasDigitalVenueAtLeastOneOffer || !venue.isVirtual
            )
            .map(venue => ({
              id: venue.nonHumanizedId.toString(),
              displayName: venue.publicName || venue.name,
            }))
        )
        setVenueOptions([ALL_VENUES_OPTION, ...sortedVenueOptions])

        setSelectedVenueId(sortedVenueOptions[0].id.toString())
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
      <Select
        handleSelection={handleChangeOfferer}
        label="Structure"
        name="offererId"
        options={offererOptions}
        selectedValue={selectedOffererId}
        isDisabled={offererOptions.length <= 1}
        className={styles['offerer-stats-select-offerer']}
      />
      {venueOptions.length > 0 && iframeUrl ? (
        <>
          <Select
            handleSelection={handleChangeVenue}
            label="Lieu"
            name="venueId"
            options={venueOptions}
            selectedValue={selectedVenueId}
            isDisabled={venueOptions.length <= 1}
            className={styles['offerer-stats-select-venue']}
          />
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
