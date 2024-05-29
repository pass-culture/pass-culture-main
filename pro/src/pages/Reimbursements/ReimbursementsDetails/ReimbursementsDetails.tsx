import { format, subMonths } from 'date-fns'
import React, { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_OFFERER_BANK_ACCOUNTS_QUERY_KEY } from 'config/swrQueryKeys'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useNotification } from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import strokeNoBookingIcon from 'icons/stroke-no-booking.svg'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { downloadFile } from 'utils/downloadFile'
import { sortByLabel } from 'utils/strings'

import { DetailsFilters } from './DetailsFilters'
import styles from './ReimbursementDetails.module.scss'

type CsvQueryParams = {
  offererId?: string
  bankAccountId?: string
  reimbursementPeriodBeginningDate?: string
  reimbursementPeriodEndingDate?: string
}

const ALL_BANK_ACCOUNTS_OPTION_ID = 'allBankAccounts'

const getCsvQueryParams = (
  bankAccount: string,
  offererId?: number,
  periodStart?: string,
  periodEnd?: string
) => {
  const params: CsvQueryParams = {}
  if (offererId) {
    params.offererId = offererId.toString()
  }
  if (periodStart) {
    params.reimbursementPeriodBeginningDate = periodStart
  }
  if (periodEnd) {
    params.reimbursementPeriodEndingDate = periodEnd
  }
  if (bankAccount && bankAccount !== ALL_BANK_ACCOUNTS_OPTION_ID) {
    params.bankAccountId = bankAccount
  }
  return new URLSearchParams(params).toString()
}

export const ReimbursementsDetails = (): JSX.Element => {
  const notify = useNotification()
  const { currentUser } = useCurrentUser()

  const today = getToday()
  const oneMonthAGo = subMonths(today, 1)
  const INITIAL_FILTERS = {
    bankAccount: ALL_BANK_ACCOUNTS_OPTION_ID,
    periodStart: format(oneMonthAGo, FORMAT_ISO_DATE_ONLY),
    periodEnd: format(today, FORMAT_ISO_DATE_ONLY),
  }

  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const { bankAccount, periodStart, periodEnd } = filters

  const isPeriodFilterSelected = periodStart && periodEnd
  const requireBankAccountFilterForAdmin =
    currentUser.isAdmin && bankAccount === ALL_BANK_ACCOUNTS_OPTION_ID

  const { selectedOfferer = null }: ReimbursementsContextProps =
    useOutletContext() || {}

  const shouldDisableButtons =
    !isPeriodFilterSelected ||
    requireBankAccountFilterForAdmin ||
    !selectedOfferer

  const bankAccountQuery = useSWR(
    selectedOfferer
      ? [GET_OFFERER_BANK_ACCOUNTS_QUERY_KEY, selectedOfferer.id]
      : null,
    ([, selectedOffererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
  )

  if (bankAccountQuery.isLoading) {
    return (
      <div className="spinner">
        <Spinner />
      </div>
    )
  }

  const bankAccountsOptions = sortByLabel(
    (bankAccountQuery.data?.bankAccounts || []).map((bankAccount) => ({
      value: bankAccount.id.toString(),
      label: bankAccount.label,
    }))
  )

  if (bankAccountsOptions.length === 0) {
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
      if (!selectedOfferer) {
        return
      }
      downloadFile(
        await api.getReimbursementsCsv(
          selectedOfferer.id,
          bankAccount !== ALL_BANK_ACCOUNTS_OPTION_ID
            ? Number(bankAccount)
            : undefined,
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
        defaultSelectId={ALL_BANK_ACCOUNTS_OPTION_ID}
        filters={filters}
        initialFilters={INITIAL_FILTERS}
        selectableOptions={bankAccountsOptions}
        setFilters={setFilters}
      >
        <Button onClick={downloadCSVFile} disabled={shouldDisableButtons}>
          Télécharger
        </Button>

        <ButtonLink
          isDisabled={shouldDisableButtons}
          link={{
            to: `/remboursements-details?${getCsvQueryParams(bankAccount, selectedOfferer?.id, periodStart, periodEnd)}`,
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
