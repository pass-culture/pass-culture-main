import React from 'react'

function BeneficiaryCell(props) {
  const { beneficiaryInfos } = props
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

export default BeneficiaryCell
