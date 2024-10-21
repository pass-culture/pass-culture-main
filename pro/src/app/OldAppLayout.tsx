import React from 'react'

import { OldLayout } from './App/layout/OldLayout'

interface OldAppLayoutProps {
  children?: React.ReactNode
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
  useOldLayout?: boolean
}

export const OldAppLayout = ({
  children,
  layout = 'basic',
}: OldAppLayoutProps) => {
  return <OldLayout layout={layout}>{children}</OldLayout>
}
