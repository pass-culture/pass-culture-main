import './Reimbursement.scss'

import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import {
  oldRoutesReimbursements,
  routesReimbursements,
} from 'app/AppRouter/subroutesReimbursements'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs'
import { ReimbursementContextProvider } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'

import styles from './Reimbursement.module.scss'
import ReimbursementsBanners from './ReimbursementsBanners'

export const Reimbursements = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const routes = isNewBankDetailsJourneyEnabled
    ? routesReimbursements
    : oldRoutesReimbursements

  return (
    <AppLayout pageName="reimbursements">
      <ReimbursementContextProvider>
        <div className={styles['reimbursements-container']}>
          <h1 className={styles['title']}>Remboursements</h1>
          <ReimbursementsBanners />
          <div>
            <ReimbursementsTabs />
            <Routes>
              {routes.map(({ path, element }) => (
                <Route key={path} path={path} element={element} />
              ))}
            </Routes>
          </div>
        </div>
      </ReimbursementContextProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
