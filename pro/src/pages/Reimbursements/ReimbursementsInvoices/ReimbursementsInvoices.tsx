import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { api } from 'apiClient/api'
import { InvoiceResponseModel, InvoiceResponseV2Model } from 'apiClient/v1'
import { BannerReimbursementsInfo } from 'components/Banner'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
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
import stylesNoResult from './InvoicesNoResult.module.scss'
import InvoicesServerError from './InvoicesServerError'
import InvoiceTable from './InvoiceTable/InvoiceTable'
import NoInvoicesYet from './NoInvoicesYet'

const ReimbursementsInvoices = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { currentUser } = useCurrentUser()
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
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [areFiltersDefault, setAreFiltersDefault] = useState(true)
  const [filterOptions, setFilterOptions] = useState<SelectOption[]>([])
  const [hasSearchedOnce, setHasSearchedOnce] = useState(false)
  const { selectedOfferer } = useReimbursementContext()

  const hasNoSearchResult =
    !hasError && invoices?.length === 0 && hasSearchedOnce

  const hasNoInvoicesYetForNonAdmin =
    !hasError &&
    !currentUser.isAdmin &&
    invoices.length === 0 &&
    !hasSearchedOnce

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
        if (isNewBankDetailsJourneyEnabled) {
          const invoices = await api.getInvoicesV2(
            periodStart,
            periodEnd,
            reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
              ? parseInt(reimbursmentPoint)
              : undefined
          )
          setInvoices(invoices)
        } else {
          const invoices = await api.getInvoices(
            periodStart,
            periodEnd,
            reimbursmentPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
              ? parseInt(reimbursmentPoint)
              : undefined
          )
          setInvoices(
            invoices.map((invoice: InvoiceResponseModel) => ({
              ...invoice,
              bankAccountLabel: invoice.reimbursementPointName,
            }))
          )
        }

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

    // We let the dependancies table empty here to have the same behavior as the previous version :
    //  data load when we arrive on the page
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const getReimbursementPointsResult = async () => {
      const result = await api.getReimbursementPoints()

      setFilterOptions(
        sortByLabel(
          result.map((item) => ({
            value: String(item.id),
            label: item.publicName || item.name,
          }))
        )
      )
    }

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

    if (isNewBankDetailsJourneyEnabled) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getBankAccountOptions()
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getReimbursementPointsResult()
    }
  }, [isNewBankDetailsJourneyEnabled, selectedOfferer])

  if (isLoading) {
    return <Spinner />
  }

  if (filterOptions.length === 0) {
    return (
      <div className={stylesNoResult['no-refunds']}>
        {isNewBankDetailsJourneyEnabled && <BannerReimbursementsInfo />}

        <SvgIcon
          src={strokeNoBookingIcon}
          alt=""
          viewBox="0 0 200 156"
          className={stylesNoResult['no-refunds-icon']}
          width="124"
        />
        <p className={stylesNoResult['no-refunds-title']}>
          Aucun remboursement à afficher
        </p>
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
        selectableOptions={filterOptions}
        setAreFiltersDefault={setAreFiltersDefault}
        setFilters={setFilters}
        setHasSearchedOnce={setHasSearchedOnce}
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
