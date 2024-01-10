import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { api } from 'apiClient/api'
import { InvoiceResponseModel } from 'apiClient/v1'
import { BannerReimbursementsInfo } from 'components/Banner'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'

import InvoicesFilters from './InvoicesFilters'
import InvoicesNoResult from './InvoicesNoResult'
import InvoicesServerError from './InvoicesServerError'
import InvoiceTable from './InvoiceTable/InvoiceTable'
import NoInvoicesYet from './NoInvoicesYet'

const ReimbursementsInvoices = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const ALL_REIMBURSEMENT_POINT_OPTION_ID = 'all'
  const { currentUser } = useCurrentUser()
  const INITIAL_FILTERS = useMemo(() => {
    const today = getToday()
    const oneMonthAgo = subMonths(today, 1)
    return {
      reimbursementPoint: ALL_REIMBURSEMENT_POINT_OPTION_ID,
      periodStart: format(oneMonthAgo, FORMAT_ISO_DATE_ONLY),
      periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
    }
  }, [])

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState<InvoiceResponseModel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [reimbursementPointsOptions, setReimbursementPointsOptions] = useState<
    SelectOption[]
  >([])

  const hasNoSearchResult = !hasError && invoices.length === 0

  const hasNoInvoicesYetForNonAdmin =
    !hasError && !currentUser.isAdmin && invoices.length === 0

  const loadInvoices = useCallback(
    async (shouldReset?: boolean) => {
      const reimbursmentPoint = shouldReset
        ? INITIAL_FILTERS.reimbursementPoint
        : filters.reimbursementPoint
      const periodStart = shouldReset
        ? INITIAL_FILTERS.periodStart
        : filters.periodStart
      const periodEnd = shouldReset
        ? INITIAL_FILTERS.periodEnd
        : filters.periodEnd

      try {
        const invoices = await api.getInvoices(
          periodStart,
          periodEnd,
          reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
            ? parseInt(reimbursmentPoint)
            : undefined
        )

        setInvoices(invoices)
        setIsLoading(false)
        setHasError(false)
      } catch (error) {
        setIsLoading(false)
        setHasError(true)
      }
    },
    [
      INITIAL_FILTERS,
      filters.periodEnd,
      filters.periodStart,
      filters.reimbursementPoint,
    ]
  )

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadInvoices()
  }, [loadInvoices])

  useEffect(() => {
    const getReimbursementPointsResult = async () => {
      const result = await api.getReimbursementPoints()

      setReimbursementPointsOptions(
        sortByLabel(
          result.map((item) => ({
            value: String(item.id),
            label: item.publicName || item.name,
          }))
        )
      )
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getReimbursementPointsResult()
  }, [])

  if (isLoading) {
    return (
      <div className="spinner">
        <Spinner />
      </div>
    )
  }

  if (reimbursementPointsOptions.length === 0) {
    return (
      <div className="no-refunds">
        {isNewBankDetailsJourneyEnabled && <BannerReimbursementsInfo />}

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
      {isNewBankDetailsJourneyEnabled && <BannerReimbursementsInfo />}
      <InvoicesFilters
        areFiltersDefault={areFiltersDefault}
        filters={filters}
        disable={hasNoInvoicesYetForNonAdmin}
        initialFilters={INITIAL_FILTERS}
        loadInvoices={loadInvoices}
        selectableOptions={reimbursementPointsOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
      />
      {hasError && <InvoicesServerError />}
      {hasNoInvoicesYetForNonAdmin && <NoInvoicesYet />}
      {hasNoSearchResult && (
        <InvoicesNoResult
          areFiltersDefault={areFiltersDefault}
          initialFilters={INITIAL_FILTERS}
          loadInvoices={loadInvoices}
          setAreFiltersDefault={setAreFiltersDefault}
          setFilters={setFilters}
        />
      )}
      {invoices.length > 0 && <InvoiceTable invoices={invoices} />}
    </>
  )
}

export default ReimbursementsInvoices
