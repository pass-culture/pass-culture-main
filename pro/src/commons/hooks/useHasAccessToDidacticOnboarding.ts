import { useEffect, useState } from 'react'

import { useRemoteConfigParams } from 'app/App/analytics/firebase'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'

export const useHasAccessToDidacticOnboarding = () => {
  const [hasAccess, setHasAccess] = useState(false)
  const isDidacticOnboardingEnabled = useActiveFeature(
    'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'
  )
  const isDidacticAbTestEnabled = useActiveFeature(
    'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST'
  )
  const { PRO_DIDACTIC_ONBOARDING_AB_TEST: firebaseUserCanSeeOnboarding } =
    useRemoteConfigParams()

  useEffect(() => {
    setHasAccess(
      isDidacticOnboardingEnabled &&
        (!isDidacticAbTestEnabled || Boolean(firebaseUserCanSeeOnboarding))
    )
  }, [
    firebaseUserCanSeeOnboarding,
    isDidacticOnboardingEnabled,
    isDidacticAbTestEnabled,
  ])

  return hasAccess
}
