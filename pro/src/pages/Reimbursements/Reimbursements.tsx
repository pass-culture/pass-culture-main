import { Outlet } from 'react-router'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

export const Reimbursements = () => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  return (
    <>
      <ReimbursementsTabs selectedOfferer={selectedAdminOfferer} />
      <Outlet />
    </>
  )
}
