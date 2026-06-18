import type {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'

import type { StepPattern } from './getSteps'

export const getLastSubmittedStepIndex = ({
  offer,
  subCategory,
  orderedSteps,
}: {
  offer: GetIndividualOfferWithAddressResponseModel | null
  subCategory?: SubcategoryResponseModel
  orderedSteps: StepPattern[]
}) => {
  let stepIndex = -1

  // No matter how the creation flow evolves, when offer is null or undefined,
  // the POST request has not been sent yet, no form has been submitted.
  if (!offer) {
    return stepIndex
  }

  for (const step of orderedSteps) {
    const { canGoBeyondStep } = step

    if (!canGoBeyondStep) {
      stepIndex++
      continue
    }

    if (canGoBeyondStep(offer, subCategory)) {
      stepIndex++
    } else {
      break
    }
  }

  return stepIndex
}
