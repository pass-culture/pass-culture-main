import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { routesReimbursements } from 'app/AppRouter/subroutesReimbursements'
import { BannerReimbursementsInfo } from 'components/Banner'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import Titles from 'ui-kit/Titles/Titles'

const Reimbursements = (): JSX.Element => {
  return (
    <>
      <Titles title="Remboursements" />

      <>
        {/* TODO: displaying condition when offerer is available here. (Done in another branch)*/}
        <AddBankAccountCallout smallCallout={true} />

        <BannerReimbursementsInfo />

        <ReimbursementsBreadcrumb />

        <Routes>
          {routesReimbursements.map(({ path, element }) => (
            <Route key={path} path={path} element={element} />
          ))}
        </Routes>
      </>
    </>
  )
}

export default Reimbursements
