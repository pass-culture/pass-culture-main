import React from 'react'
import { Outlet } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs'
import { ReimbursementContextProvider } from 'context/ReimbursementContext/ReimbursementContext'

import styles from './Reimbursement.module.scss'
import ReimbursementsBanners from './ReimbursementsBanners'

export const Reimbursements = (): JSX.Element => {
  return (
    <AppLayout pageName="reimbursements">
      <ReimbursementContextProvider>
        <div className={styles['reimbursements-container']}>
          <h1 className={styles['title']}>Gestion financière</h1>

          <ReimbursementsBanners />

          <div>
            <ReimbursementsTabs />

            <Outlet />
          </div>
        </div>
      </ReimbursementContextProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
