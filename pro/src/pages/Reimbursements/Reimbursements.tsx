import { useSelector } from 'react-redux'
import { Outlet } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const selectedOfferer = useSelector(selectCurrentOfferer)

  return (
    <BasicLayout mainHeading="Gestion financière">
      <div className={styles['reimbursements-container']}>
        <div>
          <ReimbursementsTabs selectedOfferer={selectedOfferer} />
          <Outlet context={{ selectedOfferer }} />
        </div>
      </div>
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
