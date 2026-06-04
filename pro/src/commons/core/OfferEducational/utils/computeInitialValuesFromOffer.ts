import {
  CollectiveLocationType,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
  type GetEducationalOffererResponseModel,
  type StudentLevels,
  type VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  formatShortDateForInput,
  formatTimeForInput,
  getToday,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'

import { getDefaultEducationalValues } from '../constants'
import {
  isCollectiveOfferTemplate,
  type OfferEducationalFormValues,
} from '../types'
import { buildStudentLevelsMapWithDefaultValue } from './buildStudentLevelsMapWithDefaultValue'

const computeDurationString = (
  durationMinutes: number | undefined | null
): string | undefined => {
  if (!durationMinutes) {
    return getDefaultEducationalValues().duration
  }
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
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

type CollectiveOffer =
  | GetCollectiveOfferResponseModel
  | GetCollectiveOfferTemplateResponseModel

const getContactOptions = (
  offer: CollectiveOffer
): OfferEducationalFormValues['contactOptions'] => {
  if (!isCollectiveOfferTemplate(offer)) {
    return { email: false, phone: false, form: false }
  }
  return {
    email: Boolean(offer.contactEmail),
    phone: Boolean(offer.contactPhone),
    form: Boolean(offer.contactForm || offer.contactUrl),
  }
}

const getContactFormType = (
  offer: CollectiveOffer
): OfferEducationalFormValues['contactFormType'] => {
  if (!isCollectiveOfferTemplate(offer)) {
    return undefined
  }
  return offer.contactUrl ? 'url' : 'form'
}

const getAddressAutocompleteFields = (
  offer: CollectiveOffer,
  isVenueAddress: boolean | undefined | null
) => {
  const offerAddress = offer.location?.location
  if (
    offer.location?.locationType === CollectiveLocationType.ADDRESS &&
    !isVenueAddress &&
    !offerAddress?.isManualEdition
  ) {
    const autocomplete = `${offerAddress?.street} ${offerAddress?.postalCode} ${offerAddress?.city}`
    return {
      addressAutocomplete: autocomplete,
      'search-addressAutocomplete': autocomplete,
    }
  }
  return { addressAutocomplete: '', 'search-addressAutocomplete': '' }
}

const getTemplateDateFields = (
  offer: CollectiveOffer,
  defaultValues: ReturnType<typeof getDefaultEducationalValues>
): Pick<
  OfferEducationalFormValues,
  'beginningDate' | 'endingDate' | 'hour'
> => {
  if (isCollectiveOfferTemplate(offer) && offer.dates) {
    return {
      beginningDate: formatShortDateForInput(
        toDateStrippedOfTimezone(offer.dates.start)
      ),
      endingDate: formatShortDateForInput(
        toDateStrippedOfTimezone(offer.dates.end)
      ),
      hour: formatTimeForInput(toDateStrippedOfTimezone(offer.dates.start)),
    }
  }
  return {
    beginningDate: defaultValues.beginningDate,
    endingDate: defaultValues.endingDate,
    hour: defaultValues.hour,
  }
}

export const computeInitialValuesFromOffer = (
  offerer: GetEducationalOffererResponseModel | null,
  isTemplate: boolean,
  venues: VenueListItemResponseModel[],
  offer?: CollectiveOffer,
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
  const venueAddress = defaultVenue?.location
  const offerLocationFromVenue = defaultVenue
    ? {
        locationType: CollectiveLocationType.ADDRESS,
        location: {
          isManualEdition: false,
          label: defaultVenue.publicName,
          isVenueLocation: true,
          id: defaultVenue.location?.id.toString() ?? '',
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

  const isVenueAddress = offer.location?.location?.isVenueLocation

  const offerLocationFromOffer = {
    locationType:
      offer.location?.locationType ??
      defaultEducationalFormValues.location?.locationType,
    location: {
      label: offer.location?.location?.label ?? '',
      id: isVenueAddress
        ? offer.location?.location?.id.toString()
        : 'SPECIFIC_ADDRESS',
      isVenueLocation: offer.location?.location?.isVenueLocation,
      isManualEdition: !!offer.location?.location?.isManualEdition,
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

  const offerAddress = offer.location?.location
  const address = isVenueAddress ? venueAddress : offerAddress

  const permanentOrSpecificDates = offer.dates ? 'specific_dates' : 'permanent'

  const datesType = isCollectiveOfferTemplate(offer)
    ? permanentOrSpecificDates
    : undefined

  return {
    title: offer.name,
    description: offer.description,
    duration: computeDurationString(offer.durationMinutes),
    participants,
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
    contactEmail: email ?? defaultEducationalFormValues.contactEmail,
    phone: phone ?? defaultEducationalFormValues.phone,
    bookingEmails: offer.bookingEmails.map((email) => ({
      email,
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
    ...getAddressAutocompleteFields(offer, isVenueAddress),
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
    ...getTemplateDateFields(offer, defaultEducationalFormValues),
    datesType,
    formats: offer.formats,
    contactOptions: getContactOptions(offer),
    contactFormType: getContactFormType(offer),
    contactUrl:
      isCollectiveOfferTemplate(offer) && offer.contactUrl
        ? offer.contactUrl
        : undefined,
  }
}
