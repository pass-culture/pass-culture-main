import { useSelector } from 'react-redux'
import { Outlet } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_OFFERER_NAMES_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs/ReimbursementsTabs'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const offererNamesQuery = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY],
    () => api.listOfferersNames(),
    { fallbackData: { offerersNames: [] } }
  )

  const offererQuery = useSWR(
    offererNamesQuery.isLoading && !selectedOffererId
      ? null
      : [
          GET_OFFERER_QUERY_KEY,
          selectedOffererId || offererNamesQuery.data.offerersNames[0]?.id,
        ],
    ([, offererId]) => api.getOfferer(Number(offererId))
  )

  if (
    offererNamesQuery.isLoading ||
    offererQuery.isLoading ||
    offererQuery.error
  ) {
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
