import { format, subMonths } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  GET_HAS_INVOICE_QUERY_KEY,
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import {
  selectCurrentOfferer,
  selectCurrentOffererId,
} from '@/commons/store/offerer/selectors'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'
import { isEqual } from '@/commons/utils/isEqual'
import { sortByLabel } from '@/commons/utils/strings'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { DEFAULT_INVOICES_FILTERS } from '../_constants'
import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'

export const ReimbursementsInvoices = (): JSX.Element => {
  const [, setSearchParams] = useSearchParams()
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const isCaledonian = useIsCaledonian()
  const offerer = useAppSelector(selectCurrentOfferer)

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
  const [searchFilters, setSearchFilters] = useState(INITIAL_FILTERS)

  useEffect(() => {
    const newParams = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      newParams.set(key, value)
    })
    setSearchParams(newParams, { replace: true })
  }, [filters, setSearchParams])

  const hasInvoiceQuery = useSWR(
    selectedOffererId ? [GET_HAS_INVOICE_QUERY_KEY, selectedOffererId] : null,
    ([, selectedOffererId]) => api.hasInvoice(selectedOffererId),
    { fallbackData: { hasInvoice: false } }
  )

  const hasInvoice = Boolean(hasInvoiceQuery.data.hasInvoice)

  const getInvoicesQuery = useSWR(
    selectedOffererId && hasInvoice
      ? [GET_INVOICES_QUERY_KEY, selectedOffererId, searchFilters]
      : null,
    async () => {
      const { periodStart, periodEnd, reimbursementPoint } = searchFilters
      const invoices = await api.getInvoicesV2(
        periodStart,
        periodEnd,
        reimbursementPoint !== DEFAULT_INVOICES_FILTERS.reimbursementPointId
          ? parseInt(reimbursementPoint, 10)
          : undefined,
        selectedOffererId
      )

      return invoices
    },
    {
      fallbackData: [],
    }
  )

  const getOffererBankAccountsAndAttachedVenuesQuery = useSWR(
    selectedOffererId
      ? [
          GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
          selectedOffererId,
        ]
      : null,
    ([, selectedOffererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
  )

  const handleSearch = useCallback(() => {
    setSearchFilters(filters)
  }, [filters])

  const handleResetFilters = useCallback(() => {
    setFilters(INITIAL_FILTERS)
    setSearchFilters(INITIAL_FILTERS)
  }, [INITIAL_FILTERS])

  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    getInvoicesQuery.isLoading ||
    hasInvoiceQuery.isLoading
  ) {
    return <Spinner />
  }

  const bankAccounts =
    getOffererBankAccountsAndAttachedVenuesQuery.data?.bankAccounts ?? []

  const filterOptions = sortByLabel(
    bankAccounts.map((item) => ({
      value: String(item.id),
      label: item.label,
    }))
  )

  const invoices = getInvoicesQuery.data

  return (
    <>
      {offerer?.allowedOnAdage ? (
        <BannerReimbursementsInfo />
      ) : (
        <Banner
          title="Informations exceptionnelles"
          variant={BannerVariants.WARNING}
          size="large"
          actions={[
            {
              type: 'link',
              href: 'https://passculture.zendesk.com/hc/fr/articles/4412007300369',
              label: 'Connaître les modalités de remboursement',
              isExternal: true,
              icon: fullLinkIcon,
            },
          ]}
          description={
            <>
              <p>
                Nous rencontrons exceptionnellement en cette fin d'année des
                délais de paiement allongés. Nous vous présentons toutes nos
                excuses pour la gêne occasionnée par cette situation, qui sera
                régularisée avant le 15 décembre.
              </p>
              <p>
                Pour rappel, en temps normal, le pass Culture émet un virement
                toutes les deux à trois semaines environ, à l’ensemble des
                partenaires culturels. Toutefois, ces délais courants peuvent
                être dépassés. Vous serez informés par mail dès que le paiement
                sera effectif.
              </p>
            </>
          }
        />
      )}
      <InvoicesFilters
        areFiltersDefault={isEqual(filters, INITIAL_FILTERS)}
        filters={filters}
        selectableOptions={filterOptions}
        setFilters={setFilters}
        onReset={handleResetFilters}
        onSearch={handleSearch}
      />
      {getInvoicesQuery.error ? (
        <InvoicesServerError />
      ) : (
        <InvoiceTable
          data={invoices}
          hasInvoice={hasInvoice}
          isLoading={getInvoicesQuery.isLoading}
          isCaledonian={isCaledonian}
          onFilterReset={handleResetFilters}
        />
      )}
    </>
  )
}
