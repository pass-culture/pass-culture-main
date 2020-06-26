import React from 'react'
import PropTypes from 'prop-types'

const BeneficiaryCell = ({ beneficiaryInfos }) => {
  const beneficiaryName = beneficiaryInfos.lastname.concat(' ', beneficiaryInfos.firstname)
  return (
    <div>
      <span>
        {beneficiaryName}
      </span>
      <br />
      <span className="beneficiary-subtitle">
        {beneficiaryInfos.email}
      </span>
    </div>
  )
}

BeneficiaryCell.propTypes = {
  beneficiaryInfos: PropTypes.shape({
    firstname: PropTypes.string.isRequired,
    lastname: PropTypes.string.isRequired,
  }).isRequired,
}

export default BeneficiaryCell
