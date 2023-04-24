import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { IRoute } from 'app/AppRouter/routesMap'
import routesReimbursements from 'app/AppRouter/subroutesReimbursements'
import { BannerReimbursementsInfo } from 'components/Banner'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import Titles from 'ui-kit/Titles/Titles'

const Reimbursements = (): JSX.Element => {
  return (
    <>
      <Titles title="Remboursements" />

      <>
        <BannerReimbursementsInfo />

        <ReimbursementsBreadcrumb />

        <Routes>
          {routesReimbursements.map(({ path, element }: IRoute) => (
            <Route key={path} path={path} element={element} />
          ))}
        </Routes>
      </>
    </>
  )
}

export default Reimbursements
