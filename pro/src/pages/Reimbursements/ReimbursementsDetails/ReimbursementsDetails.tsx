import { format, subMonths } from 'date-fns'
import React, { useEffect, useState } from 'react'
import { useOutletContext } from 'react-router-dom'

import { api } from 'apiClient/api'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import getVenuesForOffererAdapter from 'core/Venue/adapters/getVenuesForOffererAdapter'
import { SelectOption } from 'custom_types/form'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { downloadFile } from 'utils/downloadFile'
import { sortByLabel } from 'utils/strings'

import DetailsFilters from './DetailsFilters'
import styles from './ReimbursementDetails.module.scss'

type CsvQueryParams = {
  venueId?: string
  reimbursementPeriodBeginningDate?: string
  reimbursementPeriodEndingDate?: string
}

const ALL_VENUES_OPTION_ID = 'allVenues'

const getCsvQueryParams = (
  venue: string,
  periodStart?: string,
  periodEnd?: string
) => {
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
  return new URLSearchParams(params).toString()
}

export const ReimbursementsDetails = (): JSX.Element => {
  const notify = useNotification()
  const { currentUser } = useCurrentUser()

  const today = getToday()
  const oneMonthAGo = subMonths(today, 1)
  const INITIAL_FILTERS = {
    venue: ALL_VENUES_OPTION_ID,
    periodStart: format(oneMonthAGo, FORMAT_ISO_DATE_ONLY),
    periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const { venue, periodStart, periodEnd } = filters
  const [venuesOptions, setVenuesOptions] = useState<SelectOption[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const isPeriodFilterSelected = periodStart && periodEnd
  const requireVenueFilterForAdmin =
    currentUser.isAdmin && venue === ALL_VENUES_OPTION_ID
  const shouldDisableButtons =
    !isPeriodFilterSelected || requireVenueFilterForAdmin

  const { selectedOfferer }: ReimbursementsContextProps = useOutletContext()

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
        offererId: selectedOfferer?.id.toString(),
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

  const downloadCSVFile = async () => {
    try {
      downloadFile(
        await api.getReimbursementsCsv(
          venue !== ALL_VENUES_OPTION_ID ? Number(venue) : undefined,
          periodStart,
          periodEnd
        ),
        'remboursements_pass_culture'
      )
    } catch {
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
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
        <Button onClick={downloadCSVFile} disabled={shouldDisableButtons}>
          Télécharger
        </Button>

        <ButtonLink
          isDisabled={shouldDisableButtons}
          link={{
            to: `/remboursements-details?${getCsvQueryParams(venue, periodStart, periodEnd)}`,
            target: '_blank',
            isExternal: false,
          }}
          variant={ButtonVariant.SECONDARY}
          icon={fullLinkIcon}
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
