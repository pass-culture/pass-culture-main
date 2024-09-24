import { useTranslation } from 'react-i18next'
import { useSelector } from 'react-redux'
import { Outlet } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { ReimbursementsTabs } from 'components/ReimbursementsTabs/ReimbursementsTabs'
import {
  GET_OFFERER_NAMES_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
} from 'config/swrQueryKeys'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const { t } = useTranslation('common')
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const offererNamesQuery = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY],
    () => api.listOfferersNames(),
    { fallbackData: { offerersNames: [] } }
  )

  const offererQuery = useSWR(
    [
      GET_OFFERER_QUERY_KEY,
      selectedOffererId || offererNamesQuery.data.offerersNames[0]?.id,
    ],
    ([, offererId]) => api.getOfferer(Number(offererId))
  )

  if (offererNamesQuery.isLoading || offererQuery.isLoading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className={styles['reimbursements-container']}>
        <h1 className={styles['title']}>{t('financial_management')}</h1>
        <div>
          <ReimbursementsTabs selectedOfferer={offererQuery.data} />

          <Outlet context={{ selectedOfferer: offererQuery.data }} />
        </div>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Reimbursements
