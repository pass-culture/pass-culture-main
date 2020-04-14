import React from 'react'
import BankInformationLegacy from './BankInformationLegacy'

const BankInformation = ({ offerer }) => (
  <div className="section">
    {offerer.name}
  </div>)

BankInformation.Legacy = BankInformationLegacy
export default BankInformation
