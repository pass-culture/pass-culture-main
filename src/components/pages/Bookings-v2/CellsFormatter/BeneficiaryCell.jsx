import React from 'react'
import PropTypes from 'prop-types'

function BeneficiaryCell({ beneficiaryInfos }) {
  const beneficiaryName = beneficiaryInfos.firstname.concat(' ', beneficiaryInfos.lastname)
  return (
    <div>
      <span>
        {beneficiaryName}
      </span>
      <br />
      <span className="cell-subtitle">
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
