import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useOutletContext } from 'react-router-dom'

import { api } from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import { BannerReimbursementsInfo } from 'components/Banner/BannerReimbursementsInfo'
import { SelectOption } from 'custom_types/form'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'

import InvoicesFilters from './InvoicesFilters'
import InvoicesNoResult from './InvoicesNoResult'
import InvoicesServerError from './InvoicesServerError'
import InvoiceTable from './InvoiceTable/InvoiceTable'
import NoInvoicesYet from './NoInvoicesYet'

export const ReimbursementsInvoices = (): JSX.Element => {
  const INITIAL_FILTERS = useMemo(() => {
    const today = getToday()
    const oneMonthAgo = subMonths(today, 1)
    return {
      reimbursementPoint: DEFAULT_INVOICES_FILTERS.reimbursementPointId,
      periodStart: format(oneMonthAgo, FORMAT_ISO_DATE_ONLY),
      periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
    }
  }, [])

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [invoices, setInvoices] = useState<InvoiceResponseV2Model[]>([])
  const [offererHasInvoice, setOffererHasInvoice] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [filterOptions, setFilterOptions] = useState<SelectOption[]>([])
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)
  const { selectedOfferer }: ReimbursementsContextProps =
    useOutletContext() ?? { selectedOfferer: null }

  const hasNoSearchResult =
    (!hasError && invoices.length === 0 && hasSearchedOnce) ||
    (invoices.length === 0 && offererHasInvoice)

  const hasNoInvoicesYet = !hasError && !offererHasInvoice && !hasSearchedOnce

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
        const invoices = await api.getInvoicesV2(
          periodStart,
          periodEnd,
          reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
            ? parseInt(reimbursmentPoint)
            : undefined,
          selectedOfferer?.id
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
      selectedOfferer?.id,
    ]
  )

  useEffect(() => {
    const hasInvoice = async () => {
      if (!selectedOfferer) {
        return false
      }
      const result = await api.hasInvoice(selectedOfferer.id)
      return result.hasInvoice
    }
    const firstLoad = async () => {
      const offererHasInvoice = await hasInvoice()
      setOffererHasInvoice(offererHasInvoice)
      if (offererHasInvoice) {
        await loadInvoices()
      } else {
        setIsLoading(false)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    firstLoad()

    // We let the dependancies table empty here to have the same behavior as the previous version :
    //  data load when we arrive on the page
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedOfferer?.id])

  useEffect(() => {
    const getBankAccountOptions = async () => {
      if (!selectedOfferer) {
        return
      }
      const result = await api.getOffererBankAccountsAndAttachedVenues(
        selectedOfferer.id
      )

      setFilterOptions(
        sortByLabel(
          result.bankAccounts.map((item) => ({
            value: String(item.id),
            label: item.label,
          }))
        )
      )
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getBankAccountOptions()
  }, [selectedOfferer])

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      <BannerReimbursementsInfo />
      <InvoicesFilters
        areFiltersDefault={areFiltersDefault}
        filters={filters}
        disable={!offererHasInvoice}
        initialFilters={INITIAL_FILTERS}
        loadInvoices={loadInvoices}
        selectableOptions={filterOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
        setHasSearchedOnce={setHasSearchedOnce}
      />
      {hasError && <InvoicesServerError />}
      {hasNoInvoicesYet && <NoInvoicesYet />}
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
