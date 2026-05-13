import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import {
  ensureOffererNames,
  ensureOffererNamesValidated,
  ensureSelectedAdminOfferer,
} from '@/commons/store/user/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

export const AdministrationLayout = () => {
  const offererNames = useAppSelector(ensureOffererNames)
  const currentRoute = useCurrentRoute()
  const title = currentRoute.handle?.title
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
    <BasicLayout isAdminArea>
      <MainHeading mainHeading={title} />
      {offererNames.length > 1 && <OffererSelect />}
      {isSelectedOffererValidated ? (
        <Outlet />
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
