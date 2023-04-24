import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { BannerReimbursementsInfo } from 'components/Banner'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import Titles from 'ui-kit/Titles/Titles'

import ReimbursementsDetails from './ReimbursementsDetails/ReimbursementsDetails'
import { ReimbursementsInvoices } from './ReimbursementsInvoices'

const Reimbursements = (): JSX.Element => {
  return (
    <>
      <Titles title="Remboursements" />

      <>
        <BannerReimbursementsInfo />

        <ReimbursementsBreadcrumb />

        <Routes>
          <Route path="/justificatifs" element={<ReimbursementsInvoices />} />
          <Route path="/details" element={<ReimbursementsDetails />} />
        </Routes>
      </>
    </>
  )
}

export default Reimbursements
