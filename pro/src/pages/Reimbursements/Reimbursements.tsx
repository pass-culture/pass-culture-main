import { Outlet } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  selectCurrentOfferer,
  selectOffererNames,
} from '@/commons/store/offerer/selectors'
import { LegalEntitySelect } from '@/components/LegalEntitySelect/LegalEntitySelect'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

import styles from './Reimbursement.module.scss'

export type ReimbursementsContextProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const Reimbursements = (): JSX.Element => {
  const selectedOfferer = useAppSelector(selectCurrentOfferer)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const offererNames = useAppSelector(selectOffererNames)

  return (
    <BasicLayout
      mainHeading="Gestion financière"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && offererNames && offererNames.length > 1 && (
        <LegalEntitySelect />
      )}
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
