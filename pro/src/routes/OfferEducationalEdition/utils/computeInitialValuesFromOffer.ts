import { SubcategoryIdEnum, StudentLevels } from 'apiClient/v1'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

const computeDurationString = (
  durationMinutes: number | undefined | null
): string => {
  if (!durationMinutes) return DEFAULT_EAC_FORM_VALUES.duration
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours > 9 ? hours : `0${hours}`}:${
    minutes > 9 ? minutes : `0${minutes}`
  }`
}

export const computeInitialValuesFromOffer = (
  offer: CollectiveOffer | CollectiveOfferTemplate,
  category: string,
  subCategory: SubcategoryIdEnum
): Omit<IOfferEducationalFormValues, 'offererId' | 'venueId'> => {
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

  return {
    category,
    subCategory,
    title: offer.name,
    description: offer.description ?? DEFAULT_EAC_FORM_VALUES.description,
    duration: computeDurationString(offer.durationMinutes),
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
    notifications: offer.bookingEmails.length > 0,
    notificationEmails:
      offer.bookingEmails ?? DEFAULT_EAC_FORM_VALUES.notificationEmails,
    domains,
    interventionArea:
      offer.interventionArea ?? DEFAULT_EAC_FORM_VALUES.interventionArea,
  }
}
