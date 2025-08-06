import { Outlet } from 'react-router'

import { GetOffererResponseModel } from '@/apiClient//v1'
import { Layout } from '@/app/App/layout/Layout'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const selectedOffererId = useCurrentUser().selectedOffererId
  const {
    data: selectedOfferer,
    error: offererApiError,
    isLoading: isOffererLoading,
  } = useOfferer(selectedOffererId)

  if (isOffererLoading || offererApiError) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <Layout mainHeading="Gestion financière">
      <div className={styles['reimbursements-container']}>
        <div>
          <ReimbursementsTabs selectedOfferer={selectedOfferer} />
          <Outlet context={{ selectedOfferer }} />
        </div>
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
