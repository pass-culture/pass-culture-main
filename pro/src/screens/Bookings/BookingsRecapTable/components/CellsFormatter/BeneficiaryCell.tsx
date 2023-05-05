import React from 'react'

import { BookingRecapResponseBeneficiaryModel } from 'apiClient/v1'

import styles from './BeneficiaryCell.module.scss'

const BeneficiaryCell = ({
  beneficiaryInfos,
}: {
  beneficiaryInfos: BookingRecapResponseBeneficiaryModel
}) => {
  const beneficiaryName = [
    beneficiaryInfos.lastname,
    beneficiaryInfos.firstname,
  ]
    .join(' ')
    .trim()

  return (
    <div>
      {beneficiaryName !== '' && (
        <div data-testid="booking-cell-beneficiary-name">
          <span>{beneficiaryName}</span>
          <br />
        </div>
      )}
      <span className={styles['beneficiary-subtitle']}>
        {beneficiaryInfos.email}
      </span>
      <br />
      {beneficiaryInfos.phonenumber && (
        <span className={styles['beneficiary-subtitle']}>
          {beneficiaryInfos.phonenumber}
        </span>
      )}
    </div>
  )
}

export default BeneficiaryCell
