import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_PRO_ANONYMIZATION_ELIGIBILITY_QUERY_KEY } from '@/commons/config/swrQueryKeys'

type UseUserAnonymizationEligibilityResult = {
  isLoading: boolean
  isEligible: boolean
  isSoleUserWithOngoingActivities?: boolean
}

/**
 * Determines if a user can autonomously anonymize their personal data.
 *
 * A user is eligible for autonomous anonymization if and only if:
 * - The user is not linked to a suspended offerer
 * - The account has only pro roles
 * - The pro user is not the only owner of active offers or bookings
 */
export const useUserAnonymizationEligibility =
  (): UseUserAnonymizationEligibilityResult => {
    const { data, isLoading } = useSWR(
      [GET_PRO_ANONYMIZATION_ELIGIBILITY_QUERY_KEY],
      () => api.getProAnonymizationEligibility()
    )

    const isEligible = !!(
      !data?.hasSuspendedOfferer &&
      data?.isOnlyPro &&
      !data?.isSoleUserWithOngoingActivities
    )

    return {
      isLoading,
      isEligible,
      isSoleUserWithOngoingActivities: data?.isSoleUserWithOngoingActivities,
    }
  }
