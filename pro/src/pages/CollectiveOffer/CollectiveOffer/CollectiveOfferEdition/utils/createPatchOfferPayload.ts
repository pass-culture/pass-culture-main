import { OfferContactFormEnum } from 'apiClient/adage'
import {
  CollectiveLocationType,
  PatchCollectiveOfferBodyModel,
  PatchCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { serializeDates } from 'commons/core/OfferEducational/utils/createOfferPayload'
import { parseDuration } from 'commons/core/OfferEducational/utils/parseDuration'
import { serializeParticipants } from 'commons/core/OfferEducational/utils/serializeParticipants'
import { isEqual } from 'commons/utils/isEqual'

type PatchOfferSerializer<T> = {
  [key in keyof OfferEducationalFormValues]?: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => T
}

const baseSerializer: PatchOfferSerializer<PatchCollectiveOfferBodyModel> = {
  title: (payload, offer) => ({ ...payload, name: offer.title }),
  description: (payload, offer) => ({
    ...payload,
    description: offer.description,
  }),
  duration: (payload, offer) => ({
    ...payload,
    durationMinutes: offer.duration ? parseDuration(offer.duration) : null,
  }),
  accessibility: (payload, offer) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  notificationEmails: (payload, offer) => {
    return {
      ...payload,
      bookingEmails: offer.notificationEmails?.map((email) => email.email),
    }
  },
  offererId: (payload: PatchCollectiveOfferBodyModel) => payload,
  venueId: (payload, offer) => ({
    ...payload,
    venueId: Number(offer.venueId),
  }),
  eventAddress: (payload, offer) => {
    const eventAddressPayload = {
      ...offer.eventAddress,
      venueId: offer.eventAddress.venueId,
    }
    return offer.eventAddress.addressType
      ? {
          ...payload,
          offerVenue: eventAddressPayload,
        }
      : {}
  },
  participants: (payload, offer) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (payload, offer) => ({
    ...payload,
    contactPhone: offer.phone || null,
  }),
  email: (payload, offer) => ({
    ...payload,
    contactEmail: offer.email,
  }),
  domains: (payload, offer) => ({
    ...payload,
    domains: (offer.domains || []).map((domainIdString) =>
      Number(domainIdString)
    ),
  }),
  interventionArea: (payload, offer) => ({
    ...payload,
    interventionArea: offer.interventionArea,
  }),
  nationalProgramId: (payload, offer) => ({
    ...payload,
    nationalProgramId: offer.nationalProgramId
      ? Number(offer.nationalProgramId)
      : null,
  }),
  formats: (payload, offer) => ({
    ...payload,
    formats: offer.formats,
  }),
}

const offerLocationSerializer = (
  payload: PatchCollectiveOfferBodyModel,
  offer: OfferEducationalFormValues
) => {
  if (offer.location?.locationType === CollectiveLocationType.ADDRESS) {
    const newLocationPayload = {
      ...payload,
      location: {
        locationType: CollectiveLocationType.ADDRESS,
        address: {
          ...offer.location.address,
          banId: offer.banId ?? '',
          street: offer.street ?? '',
          postalCode: offer.postalCode ?? '',
          latitude: offer.latitude ?? '',
          longitude: offer.longitude ?? '',
          city: offer.city ?? '',
          coords: offer.coords ?? '',
        },
      },
    }

    // remove id_oa key from location object as it is useful only on a form matter
    delete newLocationPayload.location.address.id_oa
    return newLocationPayload
  }

  if (offer.location?.locationType === CollectiveLocationType.TO_BE_DEFINED) {
    return {
      ...payload,
      location: {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        locationComment: offer.location.locationComment || null,
      },
    }
  }

  return {
    ...payload,
    location: {
      locationType: CollectiveLocationType.SCHOOL,
    },
  }
}

const locationFields = [
  'location',
  'street',
  'banId',
  'postalCode',
  'city',
  'coords',
]

const locationSerializers = Object.fromEntries(
  locationFields.map((key) => [key, offerLocationSerializer])
)

const serializer: PatchOfferSerializer<PatchCollectiveOfferBodyModel> = {
  ...baseSerializer,
  ...locationSerializers,
}

const templateSerializer: PatchOfferSerializer<PatchCollectiveOfferTemplateBodyModel> =
  {
    ...serializer,
    priceDetail: (payload, offer) => ({
      ...payload,
      priceDetail: offer.priceDetail,
    }),
  }

export const createPatchOfferPayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PatchCollectiveOfferBodyModel => {
  let changedValues: PatchCollectiveOfferBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  const keysToOmmit = [
    'imageUrl',
    'imageCredit',
    'isTemplate',
    'addressAutocomplete',
  ]
  isCollectiveOaActive
    ? keysToOmmit.push('eventAddress')
    : keysToOmmit.push('location')

  offerKeys.forEach((key) => {
    if (
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-') &&
      !keysToOmmit.includes(key)
    ) {
      changedValues = {
        ...changedValues,
        ...(serializer[key]?.(changedValues, offer) ?? {}),
      }
    }
  })
  return changedValues
}

export const createPatchOfferTemplatePayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PatchCollectiveOfferTemplateBodyModel => {
  const keysToOmmit: (keyof OfferEducationalFormValues)[] = [
    'imageUrl',
    'imageCredit',
    'beginningDate',
    'endingDate',
    'datesType',
    'hour',
    'isTemplate',
    'contactFormType',
    'contactOptions',
    'addressAutocomplete',
  ]

  isCollectiveOaActive
    ? keysToOmmit.push('eventAddress')
    : keysToOmmit.push('location')

  let changedValues: PatchCollectiveOfferTemplateBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  offerKeys.forEach((key) => {
    if (
      !keysToOmmit.includes(key) &&
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-')
    ) {
      changedValues = {
        ...changedValues,
        ...(templateSerializer[key]?.(changedValues, offer) ?? {}),
      }
    }
  })

  changedValues.contactEmail =
    (offer.contactOptions?.email && offer.email) || null
  changedValues.contactPhone =
    (offer.contactOptions?.phone && offer.phone) || null
  changedValues.contactForm =
    offer.contactOptions?.form && offer.contactFormType === 'form'
      ? OfferContactFormEnum.FORM
      : null
  changedValues.contactUrl =
    offer.contactOptions?.form && offer.contactFormType === 'url'
      ? offer.contactUrl
      : null

  changedValues.dates =
    offer.datesType === 'specific_dates' &&
    offer.beginningDate &&
    offer.endingDate
      ? serializeDates(offer.beginningDate, offer.endingDate, offer.hour)
      : null

  return changedValues
}
