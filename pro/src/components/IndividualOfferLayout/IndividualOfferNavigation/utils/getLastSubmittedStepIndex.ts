import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'

import {
  RECALCULATED_PROPERTIES,
  type RecalculatedProperty,
  type StepPattern,
} from './getSteps'

export const getLastSubmittedStepIndex = ({
  offer,
  orderedSteps,
  externalConditions = {},
}: {
  offer: GetIndividualOfferResponseModel | null
  orderedSteps: StepPattern[]
  externalConditions?:
    | Record<RecalculatedProperty, boolean>
    | Record<string, never>
}) => {
  let stepIndex = -1

  // No matter how the creation flow evolves, when offer is null or undefined,
  // the POST request has not been sent yet, no form has been submitted.
  if (!offer) {
    return stepIndex
  }

  for (const step of orderedSteps) {
    const { significativeProperty } = step

    if (significativeProperty === null) {
      stepIndex++
    } else if (
      RECALCULATED_PROPERTIES.includes(
        // @ts-expect-error: this is inherently a type guard for the significativeProperty.
        significativeProperty
      )
    ) {
      if (externalConditions[significativeProperty as RecalculatedProperty]) {
        stepIndex++
      } else {
        break
      }
    } else if (
      offer[significativeProperty as keyof GetIndividualOfferResponseModel]
    ) {
      stepIndex++
    } else {
      break
    }
  }

  return stepIndex
}
