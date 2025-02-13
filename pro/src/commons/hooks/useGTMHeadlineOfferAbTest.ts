import { useRemoteConfigParams } from 'app/App/analytics/firebase'

export const useGTMHeadlineOfferAbTest = (): boolean => {
  const { PRO_EXPERIMENT_GTM_HEADLINE_OFFER: isInAbTest } =
    useRemoteConfigParams()

  return isInAbTest === 'true'
}
