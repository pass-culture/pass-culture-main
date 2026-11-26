import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type getFinanceInvoicesData,
  InvoiceDisplayedStatus,
} from '@/apiClient/v1'
import {
  GET_INVOICES_QUERY_KEY,
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { STEP_NAMES } from '@/components/ReimbursementsTabs/constants'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { getPanelId, getTabId } from '@/ui-kit/Tabs/Tabs'

import { BannerReimbursementsInfo } from './BannerReimbursementsInfo'
import { DEFAULT_INVOICES_FILTERS } from './constants'
import { InvoicesFilters } from './InvoicesFilters'
import { InvoicesServerError } from './InvoicesServerError'
import { InvoiceTable } from './InvoiceTable/InvoiceTable'

function extractStatusFilter(
  status: string | null
): InvoiceDisplayedStatus | null {
  if (status && Object.keys(InvoiceDisplayedStatus).includes(status)) {
    return status as InvoiceDisplayedStatus
  }

  return null
}

function extractFilters(
  urlParams: URLSearchParams
): Omit<getFinanceInvoicesData['query'], 'offererId'> {
  const amountPositiveOnly = urlParams.get('amountPositiveOnly')
  const amountNegativeOnly = urlParams.get('amountNegativeOnly')
  const status = extractStatusFilter(urlParams.get('status'))

  return {
    periodBeginningDate:
      urlParams.get('periodBeginningDate') ??
      DEFAULT_INVOICES_FILTERS.periodBeginningDate,
    periodEndingDate:
      urlParams.get('periodEndingDate') ??
      DEFAULT_INVOICES_FILTERS.periodEndingDate,
    ...(amountNegativeOnly && {
      amountNegativeOnly: amountNegativeOnly === 'true',
    }),
    ...(amountPositiveOnly && {
      amountPositiveOnly: amountPositiveOnly === 'true',
    }),
    ...(status && { status }),
  }
}

const ReimbursementsInvoices = (): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const isCaledonian = selectedAdminOfferer.isCaledonian
  const snackBar = useSnackBar()
  const activeStep = useActiveStep(STEP_NAMES)

  const [hideBanner, setHideBanner] = useState(
    localStorageManager.getItem(LOCAL_STORAGE_KEY.HIDE_FINANCE_BANNER) === '1'
  )

  const offererId = selectedAdminOfferer.id

  useEffect(() => {
    if (searchParams.size === 0) {
      setSearchParams(DEFAULT_INVOICES_FILTERS)
    }
  }, [searchParams, setSearchParams])

  const getInvoicesQuery = useSWR(
    offererId && searchParams.size > 0
      ? [GET_INVOICES_QUERY_KEY, offererId, searchParams]
      : null,
    async () => {
      const result = await api.getInvoices({
        query: {
          offererId: offererId,
          ...extractFilters(searchParams),
        },
      })
      return result
    },
    {
      fallbackData: { hasInvoice: false, invoices: [] },
    }
  )

  const getOffererBankAccountsAndAttachedVenuesQuery = useSWR(
    offererId
      ? [GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY, offererId]
      : null,
    ([, selectedOffererId]) =>
      api.getOffererBankAccountsAndAttachedVenues({
        path: {
          offerer_id: selectedOffererId,
        },
      }),
    {
      onError: () =>
        snackBar.error(
          'Impossible de récupérer les informations relatives à vos comptes bancaires.'
        ),
    }
  )

  const handleResetFilters = useCallback(() => {
    setSearchParams(DEFAULT_INVOICES_FILTERS)
  }, [setSearchParams])

  if (
    getOffererBankAccountsAndAttachedVenuesQuery.isLoading ||
    getInvoicesQuery.isLoading
  ) {
    return <Spinner />
  }

  const bankAccounts =
    getOffererBankAccountsAndAttachedVenuesQuery.data?.bankAccounts ?? []

  const hasInvoice = getInvoicesQuery.data.hasInvoice ?? false
  const invoices = getInvoicesQuery.data.invoices ?? []

  const onCloseBanner = () => {
    localStorageManager.setItem(LOCAL_STORAGE_KEY.HIDE_FINANCE_BANNER, '1')
    setHideBanner(true)
  }

  return (
    <div
      id={getPanelId(activeStep)}
      role="tabpanel"
      aria-labelledby={getTabId(activeStep)}
    >
      {!hideBanner && <BannerReimbursementsInfo onClose={onCloseBanner} />}

      <InvoicesFilters onReset={handleResetFilters} />

      {getInvoicesQuery.error ? (
        <InvoicesServerError />
      ) : (
        <InvoiceTable
          data={invoices}
          hasInvoice={hasInvoice}
          hasBankAccount={bankAccounts.length > 0}
          isLoading={getInvoicesQuery.isLoading}
          isCaledonian={isCaledonian}
          onFilterReset={handleResetFilters}
        />
      )}
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = ReimbursementsInvoices
