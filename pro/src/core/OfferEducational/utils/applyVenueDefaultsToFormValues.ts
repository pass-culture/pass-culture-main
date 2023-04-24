import {
  GetEducationalOffererResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import { EducationalCategories, IOfferEducationalFormValues } from '../types'

export const applyVenueDefaultsToFormValues = (
  values: IOfferEducationalFormValues,
  offerers: GetEducationalOffererResponseModel[],
  isOfferCreated: boolean,
  categories: EducationalCategories
): IOfferEducationalFormValues => {
  const venue = offerers
    ?.find(
      ({ nonHumanizedId }) => nonHumanizedId.toString() === values.offererId
    )
    ?.managedVenues?.find(
      ({ nonHumanizedId }) => nonHumanizedId.toString() === values.venueId
    )

  if (isOfferCreated || venue === undefined) {
    return { ...values }
  }

  const venueSubCategory =
    categories.educationalSubCategories.find(
      ({ id }) => venue.collectiveSubCategoryId === id
    ) ?? null

  const valuesWithNewVenueFields = {
    ...values,
    interventionArea:
      venue.collectiveInterventionArea ??
      DEFAULT_EAC_FORM_VALUES.interventionArea,
    eventAddress: {
      ...values.eventAddress,
      venueId: Number(values.venueId),
    },
    category: venueSubCategory?.categoryId ?? DEFAULT_EAC_FORM_VALUES.category,
    subCategory:
      (venue.collectiveSubCategoryId as SubcategoryIdEnum) ??
      DEFAULT_EAC_FORM_VALUES.subCategory,
  }

  // Change these fields only if offer is not created yet
  const {
    visualDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    audioDisabilityCompliant,
  } = venue

  const noDisabilityCompliant =
    !visualDisabilityCompliant &&
    !mentalDisabilityCompliant &&
    !motorDisabilityCompliant &&
    !audioDisabilityCompliant

  return {
    ...valuesWithNewVenueFields,
    accessibility: {
      visual: Boolean(visualDisabilityCompliant),
      mental: Boolean(mentalDisabilityCompliant),
      motor: Boolean(motorDisabilityCompliant),
      audio: Boolean(audioDisabilityCompliant),
      none: noDisabilityCompliant,
    },
    email: venue.collectiveEmail ?? values.email,
    phone: venue.collectivePhone ?? values.phone,
    notificationEmails: [venue.collectiveEmail ?? values.email],
  }
}
