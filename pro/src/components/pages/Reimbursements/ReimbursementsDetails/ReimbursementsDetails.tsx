import React, { useCallback, useEffect, useState } from 'react'

import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import ButtonDownloadCSV from 'new_components/ButtonDownloadCSV'
import { API_URL } from 'utils/config'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  getToday,
} from 'utils/date'

import DetailsFilters from './DetailsFilters'

type venuesOptionsType = [
  {
    id: string
    displayName: string
  }
]

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
    isCurrentUserAdmin && selectedVenue === ALL_VENUES_OPTION_ID
  const shouldDisableButtons =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

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
      <DetailsFilters
        defaultSelectDisplayName="Tous les lieux"
        defaultSelectId={ALL_VENUES_OPTION_ID}
        filters={filters}
        headerTitle="Affichage des remboursements"
        initialFilters={INITIAL_FILTERS}
        selectLabel="Lieu"
        selectName="lieu"
        selectableOptions={venuesOptions}
        setFilters={setFilters}
      >
        <ButtonDownloadCSV
          filename="remboursements_pass_culture"
          href={csvUrl}
          isDisabled={shouldDisableButtons}
          mimeType="text/csv"
        >
          Télécharger
        </ButtonDownloadCSV>
        <CsvTableButtonContainer
          href={csvUrl}
          isDisabled={shouldDisableButtons}
          url="/remboursements-details"
        >
          Afficher
        </CsvTableButtonContainer>
      </DetailsFilters>
      <p className="format-mention">
        Le fichier est au format CSV, compatible avec tous les tableurs et
        éditeurs de texte.
      </p>
    </>
  )
}

export default ReimbursementsDetails
