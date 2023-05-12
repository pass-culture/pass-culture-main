import {
  SubcategoryIdEnum,
  StudentLevels,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  IOfferEducationalFormValues,
  IEducationalCategory,
  IEducationalSubCategory,
} from '../types'

import { buildStudentLevelsMapWithDefaultValue } from './buildStudentLevelsMapWithDefaultValue'

const computeDurationString = (
  durationMinutes: number | undefined | null
): string => {
  if (!durationMinutes) {
    return DEFAULT_EAC_FORM_VALUES.duration
  }
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours > 9 ? hours : `0${hours}`}:${
    minutes > 9 ? minutes : `0${minutes}`
  }`
}

const getCategoryAndSubcategoryFromOffer = (
  categories: EducationalCategories,
  offer: CollectiveOffer | CollectiveOfferTemplate
): {
  category: IEducationalCategory | null
  subcategory: IEducationalSubCategory | null
} => {
  const subcategory =
    categories.educationalSubCategories.find(
      ({ id }) => offer.subcategoryId === id
    ) ?? null

  const category =
    categories.educationalCategories.find(
      ({ id }) => subcategory?.categoryId === id
    ) ?? null

  return {
    category,
    subcategory,
  }
}

const getInitialOffererId = (
  offerers: GetEducationalOffererResponseModel[],
  offer?: CollectiveOffer | CollectiveOfferTemplate,
  offererIdQueryParam?: string | null
): string => {
  if (offer !== undefined) {
    return offer.venue.managingOfferer.nonHumanizedId.toString()
  }

  if (offererIdQueryParam) {
    return offererIdQueryParam
  }

  if (offerers.length === 1) {
    return offerers[0].nonHumanizedId.toString()
  }

  return DEFAULT_EAC_FORM_VALUES.offererId
}

const getInitialVenueId = (
  offerers: GetEducationalOffererResponseModel[],
  offererId: string,
  offer?: CollectiveOffer | CollectiveOfferTemplate,
  venueIdQueryParam?: string | null
): string => {
  if (offer !== undefined) {
    return offer.venue.nonHumanizedId.toString()
  }

  if (venueIdQueryParam) {
    return venueIdQueryParam
  }

  if (offererId) {
    const currentOfferer = offerers.find(
      offerer => offerer.nonHumanizedId.toString() === offererId
    )

    if (currentOfferer?.managedVenues.length === 1) {
      return currentOfferer.managedVenues[0].nonHumanizedId.toString()
    }
  }

  return DEFAULT_EAC_FORM_VALUES.venueId
}

export const computeInitialValuesFromOffer = (
  categories: EducationalCategories,
  offerers: GetEducationalOffererResponseModel[],
  offer?: CollectiveOffer | CollectiveOfferTemplate,
  offererIdQueryParam?: string | null,
  venueIdQueryParam?: string | null
): IOfferEducationalFormValues => {
  const initialOffererId = getInitialOffererId(
    offerers,
    offer,
    offererIdQueryParam
  )
  const initialVenueId = getInitialVenueId(
    offerers,
    initialOffererId,
    offer,
    venueIdQueryParam
  )

  if (offer === undefined) {
    return {
      ...DEFAULT_EAC_FORM_VALUES,
      offererId: initialOffererId,
      venueId: initialVenueId,
    }
  }

  const eventAddress = offer?.offerVenue
  const participants = {
    all: Object.values(StudentLevels).every(student =>
      offer.students.includes(student)
    ),
    ...buildStudentLevelsMapWithDefaultValue((studentKey: StudentLevels) =>
      offer.students.includes(studentKey)
    ),
  }
  const email = offer.contactEmail
  const phone = offer.contactPhone
  const domains = offer.domains.map(({ id }) => id.toString())
  const { category, subcategory } = getCategoryAndSubcategoryFromOffer(
    categories,
    offer
  )

  return {
    category: category?.id ?? '',
    subCategory: (subcategory?.id ??
      DEFAULT_EAC_FORM_VALUES.subCategory) as SubcategoryIdEnum,
    title: offer.name,
    description: offer.description ?? DEFAULT_EAC_FORM_VALUES.description,
    duration: computeDurationString(offer.durationMinutes),
    // @ts-expect-error This is because we store a dehumanizedId in database.
    eventAddress: eventAddress || DEFAULT_EAC_FORM_VALUES.eventAddress,
    participants: participants || DEFAULT_EAC_FORM_VALUES.participants,
    accessibility: {
      audio: Boolean(offer.audioDisabilityCompliant),
      mental: Boolean(offer.mentalDisabilityCompliant),
      motor: Boolean(offer.motorDisabilityCompliant),
      visual: Boolean(offer.visualDisabilityCompliant),
      none:
        !offer.audioDisabilityCompliant &&
        !offer.mentalDisabilityCompliant &&
        !offer.motorDisabilityCompliant &&
        !offer.visualDisabilityCompliant,
    },
    email: email ?? DEFAULT_EAC_FORM_VALUES.email,
    phone: phone ?? DEFAULT_EAC_FORM_VALUES.phone,
    notificationEmails:
      offer.bookingEmails ??
      (email ? [email] : DEFAULT_EAC_FORM_VALUES.notificationEmails),
    domains,
    interventionArea:
      offer.interventionArea ?? DEFAULT_EAC_FORM_VALUES.interventionArea,
    venueId: initialVenueId,
    offererId: initialOffererId,
    priceDetail:
      offer.isTemplate && offer.educationalPriceDetail
        ? offer.educationalPriceDetail
        : DEFAULT_EAC_FORM_VALUES.priceDetail,
    imageUrl: offer.imageUrl || DEFAULT_EAC_FORM_VALUES.imageUrl,
    imageCredit: offer.imageCredit || DEFAULT_EAC_FORM_VALUES.imageCredit,
    'search-domains': '',
    'search-interventionArea': '',
  }
}
