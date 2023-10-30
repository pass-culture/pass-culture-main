import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import {
  oldRoutesReimbursements,
  routesReimbursements,
} from 'app/AppRouter/subroutesReimbursements'
import { ReimbursementsBreadcrumb } from 'components/ReimbursementsBreadcrumb'
import { ReimbursementContextProvider } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'

import styles from './Reimbursement.module.scss'
import ReimbursementsBanners from './ReimbursementsBanners'

const Reimbursements = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const routes = isNewBankDetailsJourneyEnabled
    ? routesReimbursements
    : oldRoutesReimbursements

  return (
    <ReimbursementContextProvider>
      <div className={styles['reimbursements-container']}>
        <h1 className={styles['title']}>Remboursements</h1>
        <ReimbursementsBanners />
        <ReimbursementsBreadcrumb />
        <div>
          <Routes>
            {routes.map(({ path, element }) => (
              <Route key={path} path={path} element={element} />
            ))}
          </Routes>
        </div>
      </div>
    </ReimbursementContextProvider>
  )
}

export default Reimbursements
