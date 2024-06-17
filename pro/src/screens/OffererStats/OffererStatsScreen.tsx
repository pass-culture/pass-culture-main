import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import { OffererStatsNoResult } from 'components/OffererStatsNoResult/OffererStatsNoResult'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { selectCurrentOffererId } from 'store/user/selectors'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Titles } from 'ui-kit/Titles/Titles'
import { sortByLabel } from 'utils/strings'

import styles from './OffererStatsScreen.module.scss'

interface OffererStatsScreenProps {
  offererOptions: SelectOption[]
}

export const OffererStatsScreen = ({
  offererOptions,
}: OffererStatsScreenProps) => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const headerOffererId = useSelector(selectCurrentOffererId)

  const [iframeUrl, setIframeUrl] = useState('')
  const [selectedOffererId, setSelectedOffererId] = useState(
    offererOptions[0].value
  )
  const [selectedVenueId, setSelectedVenueId] = useState('all')
  const [venueOptions, setVenueOptions] = useState<SelectOption[]>([])
  const ALL_VENUES_OPTION = {
    value: 'all',
    label: 'Tous les lieux',
  }

  const targetOffererId = isNewInterfaceActive
    ? headerOffererId
    : selectedOffererId

  const handleChangeOfferer = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOffererId = event.target.value
    setSelectedOffererId(selectedOffererId)
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

        if (
          !isNewInterfaceActive &&
          sortedVenueOptions.length > 0 &&
          sortedVenueOptions[0].value.toString()
        ) {
          setSelectedVenueId(sortedVenueOptions[0].value.toString())
        }
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
      <Titles title="Statistiques" />
      <p className={styles['offerer-stats-description']}>
        Vos statistiques sont calculées et mises à jour quotidiennement dans la
        nuit.
      </p>

      {!isNewInterfaceActive && (
        <FieldLayout label="Structure" name="offererId" isOptional>
          <SelectInput
            onChange={handleChangeOfferer}
            name="offererId"
            options={offererOptions}
            value={String(selectedOffererId)}
            disabled={offererOptions.length <= 1}
          />
        </FieldLayout>
      )}

      {venueOptions.length > 0 && iframeUrl ? (
        <>
          <FieldLayout label="Lieu" name="venueId" isOptional>
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
