import { format, subMonths } from 'date-fns'
import React, { useEffect, useState } from 'react'

import { VenueListItemResponseModel } from 'apiClient/v1'
import ButtonDownloadCSV from 'components/ButtonDownloadCSV'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { API_URL } from 'utils/config'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { sortByLabel } from 'utils/strings'

import DetailsFilters from './DetailsFilters'
import styles from './ReimbursementDetails.module.scss'

type CsvQueryParams = {
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
  const { selectedOfferer } = useReimbursementContext()
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const buildAndSortVenueFilterOptions = (
    venues: VenueListItemResponseModel[]
  ) =>
    sortByLabel(
      venues.map((venue) => ({
        value: venue.id.toString(),
        label: venue.isVirtual
          ? `${venue.offererName} - Offre numérique`
          : /* istanbul ignore next: TO FIX */
            venue.publicName || venue.name,
      }))
    )

  useEffect(() => {
    const loadVenues = async () => {
      const venuesResponse = await getVenuesForOffererAdapter({
        offererId: isNewBankDetailsJourneyEnabled
          ? selectedOfferer?.id.toString()
          : '',
        activeOfferersOnly: true,
      })
      const selectOptions = buildAndSortVenueFilterOptions(
        venuesResponse.payload
      )
      setVenuesOptions(selectOptions)
      setIsLoading(false)
    }
    void loadVenues()
  }, [selectedOfferer])

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
    setCsvQueryParams(new URLSearchParams(params).toString())
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
      <div className={styles['no-refunds']}>
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
        defaultSelectId={ALL_VENUES_OPTION_ID}
        filters={filters}
        initialFilters={INITIAL_FILTERS}
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
      <p className={styles['format-mention']}>
        Le fichier est au format CSV, compatible avec tous les tableurs et
        éditeurs de texte.
      </p>
    </>
  )
}

export default ReimbursementsDetails
