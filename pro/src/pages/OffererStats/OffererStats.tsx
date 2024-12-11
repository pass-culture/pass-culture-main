import { Layout } from 'app/App/layout/Layout'
import { OffererStatsScreen } from 'pages/OffererStats/OffererStats/OffererStatsScreen'

export const OffererStats = (): JSX.Element | null => {
  return (
    <Layout>
      <OffererStatsScreen />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OffererStats
