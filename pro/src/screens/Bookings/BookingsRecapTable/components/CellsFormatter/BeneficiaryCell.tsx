import React from 'react'

import {
  BookingRecapResponseBeneficiaryModel,
  EducationalRedactorResponseModel,
} from 'apiClient/v1'

const BeneficiaryCell = ({
  beneficiaryInfos,
}: {
  beneficiaryInfos:
    | BookingRecapResponseBeneficiaryModel
    | EducationalRedactorResponseModel
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
      <span className="beneficiary-subtitle">{beneficiaryInfos.email}</span>
      <br />
      {beneficiaryInfos.phonenumber && (
        <span className="beneficiary-subtitle">
          {beneficiaryInfos.phonenumber}
        </span>
      )}
    </div>
  )
}

export default BeneficiaryCell
