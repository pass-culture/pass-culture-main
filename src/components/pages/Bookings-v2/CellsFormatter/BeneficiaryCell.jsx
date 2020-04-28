import React from 'react'

function BeneficiaryCell(props) {
  const beneficiaryInfo = props.values
  return (
    <div>
        <span>
          {beneficiaryInfo.firstname} {beneficiaryInfo.lastname}
        </span>
      <br/>
      <span className={"cell-subtitle"}>
          {beneficiaryInfo.email}
        </span>
    </div>
  )
}

export default BeneficiaryCell
