import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  StudentLevels,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import {
  formatShortDateForInput,
  formatTimeForInput,
  getToday,
  toDateStrippedOfTimezone,
} from 'utils/date'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import { OfferEducationalFormValues, isCollectiveOfferTemplate } from '../types'

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

const getInitialOffererId = (
  offerers: GetEducationalOffererResponseModel[],
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
  offererIdQueryParam?: string | null
): string => {
  if (offer !== undefined) {
    return offer.venue.managingOfferer.id.toString()
  }

  if (offererIdQueryParam) {
    return offererIdQueryParam
  }

  if (offerers.length === 1) {
    return offerers[0]!.id.toString()
  }

  return DEFAULT_EAC_FORM_VALUES.offererId
}

const getInitialVenueId = (
  offerers: GetEducationalOffererResponseModel[],
  offererId: string,
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
  venueIdQueryParam?: string | null
): string => {
  if (offer !== undefined) {
    return offer.venue.id.toString()
  }

  if (venueIdQueryParam) {
    return venueIdQueryParam
  }

  if (offererId) {
    const currentOfferer = offerers.find(
      (offerer) => offerer.id.toString() === offererId
    )

    if (currentOfferer?.managedVenues.length === 1) {
      return currentOfferer.managedVenues[0]!.id.toString()
    }
  }

  return DEFAULT_EAC_FORM_VALUES.venueId
}

export const computeInitialValuesFromOffer = (
  offerers: GetEducationalOffererResponseModel[],
  isTemplate: boolean,
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
  offererIdQueryParam?: string | null,
  venueIdQueryParam?: string | null,
  isMarseilleEnabled?: boolean
): OfferEducationalFormValues => {
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
    const today = formatShortDateForInput(getToday())
    return {
      ...DEFAULT_EAC_FORM_VALUES,
      offererId: initialOffererId,
      venueId: initialVenueId,
      isTemplate,
      beginningDate: isTemplate
        ? today
        : DEFAULT_EAC_FORM_VALUES['beginningDate'],
      endingDate: isTemplate ? today : DEFAULT_EAC_FORM_VALUES['endingDate'],
      contactOptions: {
        email: false,
        form: false,
        phone: false,
      },
      contactFormType: 'form',
      contactUrl: isTemplate ? '' : undefined, //  If the field is not given an intial value, a submit would not set it as touched and the error would not appear the first time
    }
  }

  const participants = {
    all: Object.values(StudentLevels).every((student) =>
      offer.students.includes(student)
    ),
    ...buildStudentLevelsMapWithDefaultValue(
      (studentKey: StudentLevels) => offer.students.includes(studentKey),
      isMarseilleEnabled
    ),
  }
  const email = offer.contactEmail
  const phone = offer.contactPhone
  const domains = offer.domains.map(({ id }) => id.toString())

  return {
    title: offer.name,
    description: offer.description,
    duration: computeDurationString(offer.durationMinutes),
    // @ts-expect-error This is because we store a dehumanizedId in database.
    eventAddress: offer.offerVenue,
    participants: participants,
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
    notificationEmails: offer.bookingEmails,
    domains,
    interventionArea: offer.interventionArea,
    venueId: initialVenueId,
    offererId: initialOffererId,
    priceDetail:
      isCollectiveOfferTemplate(offer) && offer.educationalPriceDetail
        ? offer.educationalPriceDetail
        : DEFAULT_EAC_FORM_VALUES.priceDetail,
    imageUrl: offer.imageUrl || DEFAULT_EAC_FORM_VALUES.imageUrl,
    imageCredit: offer.imageCredit || DEFAULT_EAC_FORM_VALUES.imageCredit,
    'search-domains': '',
    'search-formats': '',
    'search-interventionArea': '',
    nationalProgramId: offer.nationalProgram?.id.toString() || '',
    isTemplate: Boolean(offer.isTemplate),
    datesType: isCollectiveOfferTemplate(offer)
      ? offer.dates
        ? 'specific_dates'
        : 'permanent'
      : undefined,
    beginningDate:
      isCollectiveOfferTemplate(offer) && offer.dates
        ? formatShortDateForInput(toDateStrippedOfTimezone(offer.dates.start))
        : DEFAULT_EAC_FORM_VALUES.beginningDate,
    endingDate:
      isCollectiveOfferTemplate(offer) && offer.dates
        ? formatShortDateForInput(toDateStrippedOfTimezone(offer.dates.end))
        : DEFAULT_EAC_FORM_VALUES.endingDate,
    hour:
      isCollectiveOfferTemplate(offer) && offer.dates
        ? formatTimeForInput(toDateStrippedOfTimezone(offer.dates.start))
        : DEFAULT_EAC_FORM_VALUES.hour,
    formats: offer.formats ?? DEFAULT_EAC_FORM_VALUES.formats,
    contactOptions: isCollectiveOfferTemplate(offer)
      ? {
          email: Boolean(offer.contactEmail),
          phone: Boolean(offer.contactPhone),
          form: Boolean(offer.contactForm || offer.contactUrl),
        }
      : undefined,
    contactFormType: isCollectiveOfferTemplate(offer)
      ? offer.contactUrl
        ? 'url'
        : 'form'
      : undefined,
    contactUrl:
      isCollectiveOfferTemplate(offer) && offer.contactUrl
        ? offer.contactUrl
        : undefined,
  }
}
