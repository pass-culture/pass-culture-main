import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  ensureOffererNames,
  ensureOffererNamesValidated,
  ensureSelectedAdminOfferer,
} from '@/commons/store/user/selectors'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

import { NonAttachedBanner } from '../../components/NonAttachedBanner/NonAttachedBanner'

// TODO (igabriele, 2026-02-10): Merge that within `<AdministrationLayout />` once `WIP_SWITCH_VENUE` FF is enabled and removed.
export const Reimbursements = () => {
  const offererNames = useAppSelector(ensureOffererNames)
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  assertOrFrontendError(
    selectedAdminOfferer,
    '`selectedAdminOfferer` is undefined'
  )

  const offererId = selectedAdminOfferer?.id
  const offererNamesValidated = useAppSelector(ensureOffererNamesValidated)
  const isSelectedOffererValidated = offererNamesValidated.some(
    (offerer) => offerer.id === offererId
  )
  return (
    <BasicLayout mainHeading="Gestion financière" isAdminArea={true}>
      {offererNames.length > 1 && <OffererSelect />}
      {isSelectedOffererValidated ? (
        <>
          <ReimbursementsTabs selectedOfferer={selectedAdminOfferer} />
          <Outlet />
        </>
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
