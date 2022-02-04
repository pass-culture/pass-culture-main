import PropTypes from 'prop-types'
import React from 'react'

const BeneficiaryCell = ({ beneficiaryInfos }) => {
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

BeneficiaryCell.propTypes = {
  beneficiaryInfos: PropTypes.shape({
    email: PropTypes.string.isRequired,
    firstname: PropTypes.string,
    lastname: PropTypes.string,
    phonenumber: PropTypes.string,
  }).isRequired,
}

export default BeneficiaryCell
