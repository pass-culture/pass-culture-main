import { CompatibleBrowsersLayout } from './CompatibleBrowsersLayout'
import { compatibleBrowsersList } from './CompatibleBrowsersList'
import type { CompatibleBrowser } from './type'

export const CompatibleBrowsers = () => {
  return (
    <CompatibleBrowsersLayout>
      {Object.values(compatibleBrowsersList).map(
        (browser: CompatibleBrowser) => (
          <div key={browser.name}>
            <h2>{browser.name}</h2>
            <p>Version minimale : {browser.minVersion}</p>
          </div>
        )
      )}
    </CompatibleBrowsersLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CompatibleBrowsers
