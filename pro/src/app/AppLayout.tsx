import React from 'react'

import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'

import { Layout } from './App/layout/Layout'
import { OldLayout } from './App/layout/OldLayout'
export interface AppLayoutProps {
  children?: React.ReactNode
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const AppLayout = ({ children, layout = 'basic' }: AppLayoutProps) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  return isNewSideBarNavigation ? (
    <Layout layout={layout}>{children}</Layout>
  ) : (
    <OldLayout layout={layout}>{children}</OldLayout>
  )
}
