import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { LoggedOutLayout } from '@/app/App/layouts/logged-out/LoggedOutLayout/LoggedOutLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'

export type CompatibleBrowsersLayoutProps = {
  children?: React.ReactNode
}

export const CompatibleBrowsersLayout = ({
  children,
}: CompatibleBrowsersLayoutProps) => {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user

  return isUserConnected ? (
    <BasicLayout mainHeading={'Navigateurs compatibles'} isFullPage={true}>
      {children}
    </BasicLayout>
  ) : (
    <LoggedOutLayout mainHeading={'Navigateurs compatibles'}>
      <section>
        <div>{children}</div>
      </section>
    </LoggedOutLayout>
  )
}
