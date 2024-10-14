import React from 'react'

import { useIsNewInterfaceActive } from 'commons/hooks/useIsNewInterfaceActive'

import { Layout, LayoutProps } from './App/layout/Layout'
import { OldLayout } from './App/layout/OldLayout'

export type AppLayoutProps = LayoutProps

export const AppLayout = ({
  children,
  mainHeading,
  layout = 'basic',
}: AppLayoutProps) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  return isNewSideBarNavigation ? (
    <Layout mainHeading={mainHeading} layout={layout}>
      {children}
    </Layout>
  ) : (
    <OldLayout mainHeading={mainHeading} layout={layout}>
      {children}
    </OldLayout>
  )
}
