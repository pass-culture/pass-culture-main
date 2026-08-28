import cn from 'classnames'

import type { BookingRecapResponseBeneficiaryModel } from '@/apiClient/v1'
import { formatPhoneNumber } from '@/commons/utils/formatPhoneNumber'

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
        <p data-testid="booking-cell-beneficiary-name">{beneficiaryName}</p>
      )}
      <p className={styles['beneficiary-subtitle']}>{beneficiaryInfos.email}</p>
      {beneficiaryInfos.phonenumber && (
        <p className={styles['beneficiary-subtitle']}>
          {formatPhoneNumber(beneficiaryInfos.phonenumber)}
        </p>
      )}
    </div>
  )
}
