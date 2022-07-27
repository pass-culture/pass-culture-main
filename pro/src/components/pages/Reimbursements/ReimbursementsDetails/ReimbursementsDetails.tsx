import React, { useEffect, useState } from 'react'

import ButtonDownloadCSV from 'new_components/ButtonDownloadCSV'
import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { API_URL } from 'utils/config'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
  getToday,
} from 'utils/date'
import { stringify } from 'utils/query-string'

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

interface ICsvQueryParams {
  venueId?: string
  reimbursementPeriodBeginningDate?: string
  reimbursementPeriodEndingDate?: string
}

const ReimbursementsDetails = ({
  isCurrentUserAdmin,
  venuesOptions,
}: IReimbursementsDetailsProps): JSX.Element => {
  const ALL_VENUES_OPTION_ID = 'allVenues'
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
  const { venue, periodStart, periodEnd } = filters
  const [csvQueryParams, setCsvQueryParams] = useState('')

  const dateFilterFormat = (date: Date) =>
    formatBrowserTimezonedDateAsUTC(date, FORMAT_ISO_DATE_ONLY)
  const isPeriodFilterSelected = periodStart && periodEnd
  const requireVenueFilterForAdmin =
    isCurrentUserAdmin && venue === ALL_VENUES_OPTION_ID
  const shouldDisableButtons =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  useEffect(() => {
    const params: ICsvQueryParams = {}
    if (periodStart)
      params.reimbursementPeriodBeginningDate = dateFilterFormat(periodStart)
    if (periodEnd)
      params.reimbursementPeriodEndingDate = dateFilterFormat(periodEnd)
    if (venue && venue !== ALL_VENUES_OPTION_ID) params.venueId = venue
    setCsvQueryParams(stringify(params))
  }, [periodEnd, periodStart, venue])

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
          href={`${API_URL}/reimbursements/csv?${csvQueryParams}`}
          isDisabled={shouldDisableButtons}
          mimeType="text/csv"
        >
          Télécharger
        </ButtonDownloadCSV>
        <ButtonLink
          isDisabled={shouldDisableButtons}
          to={`/remboursements-details?${csvQueryParams}`}
          variant={ButtonVariant.SECONDARY}
        >
          Afficher
        </ButtonLink>
      </DetailsFilters>
      <p className="format-mention">
        Le fichier est au format CSV, compatible avec tous les tableurs et
        éditeurs de texte.
      </p>
    </>
  )
}

export default ReimbursementsDetails
