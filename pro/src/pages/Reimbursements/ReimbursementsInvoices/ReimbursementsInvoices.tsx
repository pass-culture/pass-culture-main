import { format, subMonths } from 'date-fns'
import { useMemo, useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { BannerReimbursementsInfo } from 'components/Banner/BannerReimbursementsInfo'
import {
  GET_INVOICES_QUERY_KEY,
  GET_HAS_INVOICE_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { sortByLabel } from 'utils/strings'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'

import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesNoResult } from './InvoicesNoResult'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'
import { NoInvoicesYet } from './NoInvoicesYet'

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
  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)
  const { selectedOfferer = null }: ReimbursementsContextProps =
    useOutletContext()

  const getInvoicesQuery = useSWR(
    [GET_INVOICES_QUERY_KEY, selectedOfferer?.id, filters],
    async () => {
      const reimbursmentPoint = filters.reimbursementPoint
      const periodStart = filters.periodStart
      const periodEnd = filters.periodEnd

      const invoices = await api.getInvoicesV2(
        periodStart,
        periodEnd,
        reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
          ? parseInt(reimbursmentPoint)
          : undefined,
        selectedOfferer?.id
      )

      return invoices
    },
    { fallbackData: [] }
  )

  const hasInvoiceQuery = useSWR(
    [GET_HAS_INVOICE_QUERY_KEY, selectedOfferer?.id],
    async () => {
      if (!selectedOfferer) {
        return null
      }
      return await api.hasInvoice(selectedOfferer.id)
    }
  )

  const getOffererBankAccountsAndAttachedVenuesQuery = useSWR(
    [
      GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
      selectedOfferer?.id,
    ],
    () => {
      const bankAccounts = selectedOfferer?.id
        ? api.getOffererBankAccountsAndAttachedVenues(selectedOfferer.id)
        : null
      return bankAccounts
    }
  )

  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    !getOffererBankAccountsAndAttachedVenuesQuery.data ||
    getInvoicesQuery.isLoading
  ) {
    return <Spinner />
  }

  const filterOptions = sortByLabel(
    getOffererBankAccountsAndAttachedVenuesQuery.data.bankAccounts.map(
      (item) => ({
        value: String(item.id),
        label: item.label,
      })
    )
  )
  const invoices = getInvoicesQuery.data
  const hasNoSearchResult =
    !invoices.length && hasSearchedOnce && hasInvoiceQuery.data
  const hasNoInvoicesYet = !invoices.length && !hasSearchedOnce

  return (
    <>
      <BannerReimbursementsInfo />
      <InvoicesFilters
        areFiltersDefault={areFiltersDefault}
        filters={filters}
        disable={!invoices.length}
        initialFilters={INITIAL_FILTERS}
        selectableOptions={filterOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
        setHasSearchedOnce={setHasSearchedOnce}
      />
      {getInvoicesQuery.error && <InvoicesServerError />}
      {hasNoInvoicesYet && <NoInvoicesYet />}
      {hasNoSearchResult && (
        <InvoicesNoResult
          areFiltersDefault={areFiltersDefault}
          initialFilters={INITIAL_FILTERS}
          setAreFiltersDefault={setAreFiltersDefault}
          setFilters={setFilters}
        />
      )}
      {invoices.length && <InvoiceTable invoices={invoices} />}
    </>
  )
}
