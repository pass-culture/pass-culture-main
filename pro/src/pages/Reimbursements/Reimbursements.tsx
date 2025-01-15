import { Outlet } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import { GET_OFFERER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs/ReimbursementsTabs'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const selectedOffererId = useCurrentUser().selectedOffererId

  const offererQuery = useSWR(
    !selectedOffererId ? null : [GET_OFFERER_QUERY_KEY, selectedOffererId],
    ([, offererId]) => api.getOfferer(Number(offererId))
  )

  if (offererQuery.isLoading || offererQuery.error) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <Layout>
      <div className={styles['reimbursements-container']}>
        <h1 className={styles['title']}>Gestion financière</h1>
        <div>
          <ReimbursementsTabs selectedOfferer={offererQuery.data} />

          <Outlet context={{ selectedOfferer: offererQuery.data }} />
        </div>
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
