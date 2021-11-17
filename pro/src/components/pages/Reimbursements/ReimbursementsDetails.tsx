import isEqual from 'lodash.isequal'
import React, { useCallback, useEffect, useState } from 'react'

import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import { API_URL } from 'utils/config'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  getToday,
} from 'utils/date'

type venuesOptionsType = [
  {
    id: string
    displayName: string
  }
]

type filtersType = {
  venue: string
  periodStart: Date
  periodEnd: Date
}

interface IReimbursementsDetailsProps {
  isCurrentUserAdmin: boolean
  venuesOptions: venuesOptionsType
}

const ReimbursementsDetails = ({
  isCurrentUserAdmin,
  venuesOptions,
}: IReimbursementsDetailsProps): JSX.Element => {
  const ALL_VENUES_OPTION_ID = 'allVenues'
  const INITIAL_CSV_URL = `${API_URL}/reimbursements/csv`
  const today = getToday()
  const oneMonthAGo = new Date(
    today.getFullYear(),
    today.getMonth() - 1,
    today.getDate()
  )
  const INITIAL_FILTERS = {
    venue: ALL_VENUES_OPTION_ID,
    periodStart: oneMonthAGo,
    periodEnd: today,
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const {
    venue: selectedVenue,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters
  const [csvUrl, setCsvUrl] = useState(INITIAL_CSV_URL)

  const dateFilterFormat = (date: Date) =>
    formatBrowserTimezonedDateAsUTC(date, FORMAT_ISO_DATE_ONLY)
  const isPeriodFilterSelected = selectedPeriodStart && selectedPeriodEnd
  const requireVenueFilterForAdmin =
    isCurrentUserAdmin && selectedVenue === 'allVenues'
  const shouldDisableButtons =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  function resetFilters() {
    setFilters(INITIAL_FILTERS)
  }

  const buildCsvUrlWithParameters = useCallback(
    (
      selectedVenue: string,
      selectedPeriodStart: Date,
      selectedPeriodEnd: Date
    ) => {
      const url = new URL(INITIAL_CSV_URL)

      if (selectedVenue && selectedVenue !== ALL_VENUES_OPTION_ID) {
        url.searchParams.set('venueId', selectedVenue)
      }

      if (selectedPeriodStart) {
        url.searchParams.set(
          'reimbursementPeriodBeginningDate',
          dateFilterFormat(selectedPeriodStart)
        )
      }

      if (selectedPeriodEnd) {
        url.searchParams.set(
          'reimbursementPeriodEndingDate',
          dateFilterFormat(selectedPeriodEnd)
        )
      }

      return url.toString()
    },
    [INITIAL_CSV_URL]
  )

  const setVenueFilter = useCallback(
    event => {
      const venueId = event.target.value
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        venue: venueId,
      }))
    },
    [setFilters]
  )

  const setStartDateFilter = useCallback(
    startDate => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodStart: startDate,
      }))
    },
    [setFilters]
  )

  const setEndDateFilter = useCallback(
    endDate => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodEnd: endDate,
      }))
    },
    [setFilters]
  )

  useEffect(() => {
    setCsvUrl(
      buildCsvUrlWithParameters(
        selectedVenue,
        selectedPeriodStart,
        selectedPeriodEnd
      )
    )
  }, [
    buildCsvUrlWithParameters,
    selectedPeriodEnd,
    selectedPeriodStart,
    selectedVenue,
  ])

  return (
    <>
      <div className="header">
        <h2 className="header-title">Affichage des remboursements</h2>
        <button
          className="tertiary-button reset-filters"
          disabled={isEqual(filters, INITIAL_FILTERS)}
          onClick={resetFilters}
          type="button"
        >
          Réinitialiser les filtres
        </button>
      </div>

      <div className="filters">
        <Select
          defaultOption={{
            displayName: 'Tous les lieux',
            id: ALL_VENUES_OPTION_ID,
          }}
          handleSelection={setVenueFilter}
          label="Lieu"
          name="lieu"
          options={venuesOptions}
          selectedValue={selectedVenue}
        />
        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={false}
          label="Période"
          maxDateEnding={getToday()}
          periodBeginningDate={selectedPeriodStart}
          periodEndingDate={selectedPeriodEnd}
          todayDate={getToday()}
        />
      </div>

      <div className="button-group">
        <span className="button-group-separator" />
        <div className="button-group-buttons">
          <DownloadButtonContainer
            filename="remboursements_pass_culture"
            href={csvUrl}
            isDisabled={shouldDisableButtons}
            mimeType="text/csv"
          >
            Télécharger
          </DownloadButtonContainer>
          <CsvTableButtonContainer
            href={csvUrl}
            isDisabled={shouldDisableButtons}
          >
            Afficher
          </CsvTableButtonContainer>
        </div>
      </div>

      <p className="format-mention">
        Le fichier est au format CSV, compatible avec tous les tableurs et
        éditeurs de texte.
      </p>
    </>
  )
}

export default ReimbursementsDetails
