import { format, subMonths } from 'date-fns'
import React, { useCallback, useEffect, useState } from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import ButtonDownloadCSV from 'components/ButtonDownloadCSV'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { API_URL } from 'utils/config'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { stringify } from 'utils/query-string'
import { sortByLabel } from 'utils/strings'

import DetailsFilters from './DetailsFilters'

interface CsvQueryParams {
  venueId?: string
  reimbursementPeriodBeginningDate?: string
  reimbursementPeriodEndingDate?: string
}

const ReimbursementsDetails = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const ALL_VENUES_OPTION_ID = 'allVenues'
  const today = getToday()
  const oneMonthAGo = subMonths(today, 1)
  const INITIAL_FILTERS = {
    venue: ALL_VENUES_OPTION_ID,
    periodStart: format(oneMonthAGo, FORMAT_ISO_DATE_ONLY),
    periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const { venue, periodStart, periodEnd } = filters
  const [csvQueryParams, setCsvQueryParams] = useState('')
  const [venuesOptions, setVenuesOptions] = useState<SelectOption[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const isPeriodFilterSelected = periodStart && periodEnd
  const requireVenueFilterForAdmin =
    currentUser.isAdmin && venue === ALL_VENUES_OPTION_ID
  const shouldDisableButtons =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  const buildAndSortVenueFilterOptions = (
    venues: VenueListItemResponseModel[]
  ) =>
    sortByLabel(
      venues.map(venue => ({
        value: venue.id.toString(),
        label: venue.isVirtual
          ? `${venue.offererName} - Offre numérique`
          : /* istanbul ignore next: TO FIX */
            venue.publicName || venue.name,
      }))
    )

  const loadVenues = useCallback(async () => {
    const venuesResponse = await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    const selectOptions = buildAndSortVenueFilterOptions(venuesResponse.payload)
    setVenuesOptions(selectOptions)
    setIsLoading(false)
  }, [setVenuesOptions])

  useEffect(() => {
    loadVenues()
  }, [loadVenues])

  useEffect(() => {
    const params: CsvQueryParams = {}
    if (periodStart) {
      params.reimbursementPeriodBeginningDate = periodStart
    }
    if (periodEnd) {
      params.reimbursementPeriodEndingDate = periodEnd
    }
    if (venue && venue !== ALL_VENUES_OPTION_ID) {
      params.venueId = venue
    }
    setCsvQueryParams(stringify(params))
  }, [periodEnd, periodStart, venue])
  if (isLoading) {
    return (
      <div className="spinner">
        <Spinner />
      </div>
    )
  }
  if (venuesOptions.length === 0) {
    return (
      <div className="no-refunds">
        <SvgIcon
          src={strokeNoBookingIcon}
          alt=""
          viewBox="0 0 200 156"
          className="no-refunds-icon"
          width="124"
        />
        <span>Aucun remboursement à afficher</span>
      </div>
    )
  }
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
          link={{
            to: `/remboursements-details?${csvQueryParams}`,
            isExternal: false,
          }}
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
