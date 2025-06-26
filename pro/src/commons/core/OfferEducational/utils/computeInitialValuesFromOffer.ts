import {
  CollectiveLocationType,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
  StudentLevels,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  formatShortDateForInput,
  formatTimeForInput,
  getToday,
  toDateStrippedOfTimezone,
} from 'commons/utils/date'

import { getDefaultEducationalValues } from '../constants'
import { isCollectiveOfferTemplate, OfferEducationalFormValues } from '../types'

import { buildStudentLevelsMapWithDefaultValue } from './buildStudentLevelsMapWithDefaultValue'

const computeDurationString = (
  durationMinutes: number | undefined | null
): string | undefined => {
  if (!durationMinutes) {
    return getDefaultEducationalValues().duration
  }
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours > 9 ? hours : `0${hours}`}:${
    minutes > 9 ? minutes : `0${minutes}`
  }`
}

const getInitialOffererId = (
  offerer: GetEducationalOffererResponseModel | null,
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
): string => {
  if (offer !== undefined) {
    return offer.venue.managingOfferer.id.toString()
  }

  if (offerer) {
    return offerer.id.toString()
  }

  return getDefaultEducationalValues().offererId
}

const getInitialVenueId = (
  offerer: GetEducationalOffererResponseModel | null,
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
    if (offerer?.managedVenues.length === 1) {
      return offerer.managedVenues[0].id.toString()
    }
  }

  return getDefaultEducationalValues().venueId
}

export const computeInitialValuesFromOffer = (
  offerer: GetEducationalOffererResponseModel | null,
  isTemplate: boolean,
  venues: VenueListItemResponseModel[],
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
  venueIdQueryParam?: string | null,
  isMarseilleEnabled?: boolean
): OfferEducationalFormValues => {
  const initialOffererId = getInitialOffererId(offerer, offer)
  const initialVenueId = getInitialVenueId(
    offerer,
    initialOffererId,
    offer,
    venueIdQueryParam
  )

  const defaultEducationalFormValues =
    getDefaultEducationalValues(isMarseilleEnabled)

  const defaultVenue = venues.find((v) => v.id.toString() === initialVenueId)
  const venueAddress = defaultVenue?.address
  const offerLocationFromVenue = defaultVenue
    ? {
        locationType: CollectiveLocationType.ADDRESS,
        address: {
          isVenueAddress: true,
          isManualEdition: false,
          label: defaultVenue.name,
          id_oa: defaultVenue.address?.id_oa.toString() ?? '',
        },
      }
    : defaultEducationalFormValues.location

  if (offer === undefined) {
    const today = formatShortDateForInput(getToday())
    return {
      ...defaultEducationalFormValues,
      city: venueAddress?.city,
      street: venueAddress?.street,
      postalCode: venueAddress?.postalCode,
      latitude: venueAddress?.latitude.toString(),
      longitude: venueAddress?.longitude.toString(),
      banId: venueAddress?.banId,
      offererId: initialOffererId,
      venueId: initialVenueId,
      location: offerLocationFromVenue,
      isTemplate,
      beginningDate: isTemplate
        ? today
        : defaultEducationalFormValues['beginningDate'],
      endingDate: isTemplate
        ? today
        : defaultEducationalFormValues['endingDate'],
      contactOptions: {
        email: false,
        form: false,
        phone: false,
      },
      contactFormType: 'form',
      contactUrl: isTemplate ? '' : undefined, //  If the field is not given an initial value, a submit would not set it as touched and the error would not appear the first time
    }
  }

  const isVenueAddress =
    offer.location?.address?.id_oa === defaultVenue?.address?.id_oa

  const offerLocationFromOffer = {
    locationType:
      offer.location?.locationType ??
      defaultEducationalFormValues.location?.locationType,
    address: {
      isVenueAddress,
      label: offer.location?.address?.label ?? '',
      id_oa: isVenueAddress
        ? offer.location?.address?.id_oa.toString()
        : 'SPECIFIC_ADDRESS',
      isManualEdition: !!offer.location?.address?.isManualEdition,
    },
    locationComment: offer.location?.locationComment,
  }

  const participants = buildStudentLevelsMapWithDefaultValue(
    (studentKey: StudentLevels) => offer.students.includes(studentKey),
    isMarseilleEnabled
  )

  const email = offer.contactEmail
  const phone = offer.contactPhone
  const domains = offer.domains.map(({ id }) => id.toString())

  const offerAddress = offer.location?.address
  const address = isVenueAddress ? venueAddress : offerAddress

  return {
    title: offer.name,
    description: offer.description,
    duration: computeDurationString(offer.durationMinutes),
    eventAddress: {
      ...offer.offerVenue,
      venueId: offer.offerVenue.venueId || Number(initialVenueId),
    },
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
    email: email ?? defaultEducationalFormValues.email,
    phone: phone ?? defaultEducationalFormValues.phone,
    notificationEmails: offer.bookingEmails.map((email) => ({
      email: email,
    })),
    domains,
    interventionArea: offer.interventionArea,
    venueId: initialVenueId,
    offererId: initialOffererId,
    // If the venue's OA selected at step 1 is the same than the one we have saved in offer draft,
    // then set this OA id in formik field (so it will be checked by default)
    // Else, we can assume it's an "other" address
    location: isVenueAddress ? offerLocationFromVenue : offerLocationFromOffer,
    city: address?.city,
    street: address?.street,
    postalCode: address?.postalCode,
    latitude: address?.latitude.toString(),
    longitude: address?.longitude.toString(),
    banId: address?.banId,
    coords: `${address?.latitude}, ${address?.longitude}`,
    // if offer location is a specific address selected with address API we should fill address autocomplete fields
    ...(offer.location?.locationType === CollectiveLocationType.ADDRESS &&
    !isVenueAddress &&
    !offerAddress?.isManualEdition
      ? {
          addressAutocomplete: `${offerAddress?.street} ${offerAddress?.postalCode} ${offerAddress?.city}`,
          'search-addressAutocomplete': `${offerAddress?.street} ${offerAddress?.postalCode} ${offerAddress?.city}`,
        }
      : { addressAutocomplete: '', 'search-addressAutocomplete': '' }),
    priceDetail:
      isCollectiveOfferTemplate(offer) && offer.educationalPriceDetail
        ? offer.educationalPriceDetail
        : defaultEducationalFormValues.priceDetail,
    imageUrl: offer.imageUrl || defaultEducationalFormValues.imageUrl,
    imageCredit: offer.imageCredit || defaultEducationalFormValues.imageCredit,
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
        : defaultEducationalFormValues.beginningDate,
    endingDate:
      isCollectiveOfferTemplate(offer) && offer.dates
        ? formatShortDateForInput(toDateStrippedOfTimezone(offer.dates.end))
        : defaultEducationalFormValues.endingDate,
    hour:
      isCollectiveOfferTemplate(offer) && offer.dates
        ? formatTimeForInput(toDateStrippedOfTimezone(offer.dates.start))
        : defaultEducationalFormValues.hour,
    formats: offer.formats,
    contactOptions: isCollectiveOfferTemplate(offer)
      ? {
          email: Boolean(offer.contactEmail),
          phone: Boolean(offer.contactPhone),
          form: Boolean(offer.contactForm || offer.contactUrl),
        }
      : {
          email: false,
          phone: false,
          form: false,
        },
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
