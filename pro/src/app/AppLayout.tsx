import React from 'react'

import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'

import { Layout } from './App/layout/Layout'
import { OldLayout } from './App/layout/OldLayout'
export interface AppLayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}

export const AppLayout = ({
  children,
  className,
  pageName = 'Accueil',
  layout = 'basic',
}: AppLayoutProps) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  return isNewSideBarNavigation ? (
    <Layout className={className} pageName={pageName} layout={layout}>
      {children}
    </Layout>
  ) : (
    <OldLayout className={className} pageName={pageName} layout={layout}>
      {children}
    </OldLayout>
  )
}
