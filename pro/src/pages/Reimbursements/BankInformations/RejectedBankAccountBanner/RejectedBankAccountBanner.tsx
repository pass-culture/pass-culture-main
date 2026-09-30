import type {
  BankAccountResponseModel,
  RejectedBankAccountResponseModel,
} from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Divider } from '@/ui-kit/Divider/Divider'

import { RejectedBankAccountBannerForm } from '../RejectedBankAccountBannerForm/RejectedBankAccountBannerForm'
import styles from './RejectedBankAccountBanner.module.scss'

export type RejectedBankAccountBannerProps = {
  rejectedBankAccount: RejectedBankAccountResponseModel
  bankAccounts: BankAccountResponseModel[]
  onAddBankAccount: () => void
  onReplaceBankAccount: (
    bankAccountId: number,
    venuesIds: number[]
  ) => Promise<boolean>
}

export const RejectedBankAccountBanner = ({
  rejectedBankAccount,
  bankAccounts,
  onAddBankAccount,
  onReplaceBankAccount,
}: RejectedBankAccountBannerProps): JSX.Element => {
  const getBankAccountLabel = (label: string, iban: string) =>
    `${label} (IBAN **** ${iban.slice(-4)})`

  const getDetachedVenuesDescription = (venueNames: string[]) => {
    if (venueNames.length === 0) {
      return ''
    }

    return (
      <>
        {venueNames.map((venueName, index) => (
          <span key={venueName}>
            {venueNames.length > 1 && index === venueNames.length - 1 && ' et '}

            <span key={venueName} className={styles['venue-name']}>
              {venueName}
            </span>

            {venueNames.length > 1 && index < venueNames.length - 2 && ', '}
          </span>
        ))}

        {pluralizeFr(
          venueNames.length,
          ' en a été détachée.',
          ' en ont été détachées.'
        )}
      </>
    )
  }

  const getRejectedBankAccountDescription = (
    bankAccount: RejectedBankAccountResponseModel
  ) => (
    <>
      <p className={styles['banner-content']} data-testid="banner-content">
        {`Le compte bancaire ${getBankAccountLabel(bankAccount.label, bankAccount.obfuscatedIban)} a été rejeté lors du virement et supprimé de cette page. `}
        {getDetachedVenuesDescription(
          bankAccount.detachedVenues.map((v) => v.publicName)
        )}
      </p>

      <p>
        Choisissez un compte de remplacement :
        {pluralizeFr(
          bankAccount.detachedVenues.length,
          ' cette structure y sera rattachée ',
          ` ces ${bankAccount.detachedVenues.length} structures y seront rattachées `
        )}
        et un nouveau virement sera émis.
      </p>

      <Divider />

      {bankAccounts.length > 0 && (
        <RejectedBankAccountBannerForm
          bankAccounts={bankAccounts}
          onAddBankAccount={onAddBankAccount}
          onReplaceBankAccount={(bankAccountId) =>
            onReplaceBankAccount(
              bankAccountId,
              bankAccount.detachedVenues.map((venue) => venue.id)
            )
          }
        />
      )}
    </>
  )

  return (
    <Banner
      key={rejectedBankAccount.id}
      title={`Le compte bancaire du virement ${rejectedBankAccount.rejectedSettlementLabel} a été rejeté`}
      description={getRejectedBankAccountDescription(rejectedBankAccount)}
      variant={BannerVariants.ERROR}
    />
  )
}
