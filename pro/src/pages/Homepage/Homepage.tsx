import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import { NewHomepage } from './NewHomepage'
import { OldHomepage } from './OldHomepage'

export const Homepage = (): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const shouldDisplayNewHomepage =
    useActiveFeature('WIP_ENABLE_NEW_PRO_HOME') && withSwitchVenueFeature

  return shouldDisplayNewHomepage ? <NewHomepage /> : <OldHomepage />
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Homepage
