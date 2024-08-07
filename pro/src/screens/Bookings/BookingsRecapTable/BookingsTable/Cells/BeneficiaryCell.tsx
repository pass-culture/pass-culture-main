import cn from 'classnames'

import { BookingRecapResponseBeneficiaryModel } from 'apiClient/v1'

import styles from './BeneficiaryCell.module.scss'

export interface BeneficiaryCellProps {
  beneficiaryInfos: BookingRecapResponseBeneficiaryModel
  className?: string
}

export const BeneficiaryCell = ({
  beneficiaryInfos,
  className,
}: BeneficiaryCellProps) => {
  const beneficiaryName = [
    beneficiaryInfos.lastname,
    beneficiaryInfos.firstname,
  ]
    .join(' ')
    .trim()

  return (
    <div className={cn(className)}>
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
