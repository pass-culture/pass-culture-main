import { useEffect } from 'react'
import { useNavigate } from 'react-router'

import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

export const SubscriptionRedirection = (): JSX.Element | null => {
  const isWelcomeCarouselEnabled = useActiveFeature('WIP_PRE_SIGNUP_INFO')
  const navigate = useNavigate()
  useEffect(() => {
    if (isWelcomeCarouselEnabled) {
      navigate('/bienvenue')
    } else {
      navigate('/inscription/compte/creation')
    }
  }, [isWelcomeCarouselEnabled, navigate])

  return null
}
