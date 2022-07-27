import React from 'react'

import InputError from 'components/layout/inputs/Errors/InputError'
import { RadioInput } from 'components/layout/inputs/RadioInput/RadioInput'
import {
  OFFER_WITHDRAWAL_TYPE_LABELS,
  OFFER_WITHDRAWAL_TYPE_OPTIONS,
} from 'core/Offers'

import styles from './OfferWithdrawalTypeOptions.module.scss'

interface IOfferWithdrawalTypeOptionsProps {
  withdrawalType?: OFFER_WITHDRAWAL_TYPE_OPTIONS
  error?: string
  updateWithdrawalType: (event: React.ChangeEvent<HTMLInputElement>) => void
}

export const OfferWithdrawalTypeOptions = ({
  withdrawalType,
  updateWithdrawalType,
  error,
}: IOfferWithdrawalTypeOptionsProps): JSX.Element => {
  const handleRadioInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (event?.target?.value === withdrawalType) {
      return
    }
    updateWithdrawalType(event)
  }

  return (
    <section className="form-row">
      <p>Comment les billets, places seront-ils transmis ?</p>
      <div className={styles['form-row-radio']}>
        <RadioInput
          checked={withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET}
          disabled={false}
          error={error}
          label={
            OFFER_WITHDRAWAL_TYPE_LABELS[
              OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET
            ]
          }
          name="withdrawalType"
          onChange={handleRadioInputChange}
          value={OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET}
        />
      </div>
      <div className={styles['form-row-radio']}>
        <RadioInput
          checked={withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL}
          disabled={false}
          error={error}
          label={
            OFFER_WITHDRAWAL_TYPE_LABELS[OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL]
          }
          name="withdrawalType"
          onChange={handleRadioInputChange}
          value={OFFER_WITHDRAWAL_TYPE_OPTIONS.BY_EMAIL}
        />
      </div>
      <div className={styles['form-row-radio']}>
        <RadioInput
          checked={withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE}
          disabled={false}
          error={error}
          label={
            OFFER_WITHDRAWAL_TYPE_LABELS[OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE]
          }
          name="withdrawalType"
          onChange={handleRadioInputChange}
          value={OFFER_WITHDRAWAL_TYPE_OPTIONS.ON_SITE}
        />
      </div>
      {error && (
        <div className={styles['form-row-radio']}>
          <InputError>{error}</InputError>
        </div>
      )}
    </section>
  )
}
