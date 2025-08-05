import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

export const useHasAccessToDidacticOnboarding = () => {
  const [hasAccess, setHasAccess] = useState<boolean | undefined>()
  const isDidacticOnboardingEnabled = useActiveFeature(
    'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING'
  )
  const isDidacticAbTestEnabled = useActiveFeature(
    'WIP_ENABLE_PRO_DIDACTIC_ONBOARDING_AB_TEST'
  )

  const currentUser = useSelector(selectCurrentUser)
  const isUserIncludedinDidacticOnboarding = Boolean(
    currentUser && currentUser.id % 2 === 0
  )

  useEffect(() => {
    setHasAccess(
      isDidacticOnboardingEnabled &&
        (!isDidacticAbTestEnabled || isUserIncludedinDidacticOnboarding)
    )
  }, [
    isUserIncludedinDidacticOnboarding,
    isDidacticOnboardingEnabled,
    isDidacticAbTestEnabled,
  ])

  return hasAccess
}
