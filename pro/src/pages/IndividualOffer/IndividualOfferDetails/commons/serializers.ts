import {
  type ArtistOfferLinkBodyModel,
  type ArtistOfferLinkResponseModel,
  ArtistType,
  type PatchOfferBodyModel,
  type PostOfferBodyModel,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { normalizeRequestBodyProps } from '@/commons/utils/normalizeRequestBodyProps'
import { trimStringsInObject } from '@/commons/utils/trimStringsInObject'

import type { DetailsFormValues } from './types'

export const serializeDurationMinutes = (
  durationHour: string
): number | null => {
  /* istanbul ignore next: DEBT, TO FIX */
  if (durationHour.trim().length === 0) {
    return null
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export function deSerializeDurationMinutes(durationMinute: number): string {
  const hours = Math.floor(durationMinute / 60)
    .toString()
    .padStart(2, '0')
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

export const serializeExtraData = (
  formValues: DetailsFormValues,
  isOfferArtistsFeatureActive: boolean
) => {
  const validArtistOfferLinks = formValues.artistOfferLinks.filter((artist) =>
    artist.artistName?.trim()
  )

  const shouldUseArtistOfferLinks =
    isOfferArtistsFeatureActive && !formValues.productId

  const author = shouldUseArtistOfferLinks
    ? validArtistOfferLinks
        .filter((link) => link.artistType === ArtistType.AUTHOR)
        .map((link) => link.artistName)
        .join(', ')
    : formValues.author

  const stageDirector = shouldUseArtistOfferLinks
    ? validArtistOfferLinks
        .filter((link) => link.artistType === ArtistType.STAGE_DIRECTOR)
        .map((link) => link.artistName)
        .join(', ')
    : formValues.stageDirector

  const performer = shouldUseArtistOfferLinks
    ? validArtistOfferLinks
        .filter((link) => link.artistType === ArtistType.PERFORMER)
        .map((link) => link.artistName)
        .join(', ')
    : formValues.performer

  return normalizeRequestBodyProps({
    author,
    gtl_id: formValues.gtl_id,
    performer,
    showType: formValues.showType,
    showSubType: formValues.showSubType,
    speaker: formValues.speaker,
    stageDirector,
    visa: formValues.visa,
    ean: formValues.ean,
  })
}

const serializeArtistOfferLinks = (
  artistOfferLinks: ArtistOfferLinkResponseModel[]
): ArtistOfferLinkBodyModel[] | undefined => {
  const links: ArtistOfferLinkBodyModel[] = []
  const validArtistOfferLinks = artistOfferLinks.filter((artist) =>
    artist.artistName?.trim()
  )
  validArtistOfferLinks.forEach((link) => {
    links.push({
      artistId: link.artistId,
      artistName: link.artistName.trim(),
      artistType: link.artistType,
    })
  })

  return links
}

export function serializeDetailsPostData(
  formValues: DetailsFormValues,
  isOfferArtistsFeatureActive: boolean
): PostOfferBodyModel {
  assertOrFrontendError(
    formValues.accessibility,
    '`formValues.accessibility` is undefined'
  )

  return trimStringsInObject({
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    venueId: Number(formValues.venueId),
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues, isOfferArtistsFeatureActive),
    productId: formValues.productId ? Number(formValues.productId) : undefined,
    audioDisabilityCompliant: formValues.accessibility.audio,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    visualDisabilityCompliant: formValues.accessibility.visual,
    artistOfferLinks: serializeArtistOfferLinks(formValues.artistOfferLinks),
  })
}

export function serializeDetailsPatchData(
  formValues: DetailsFormValues,
  isOfferArtistsFeatureActive: boolean
): PatchOfferBodyModel {
  assertOrFrontendError(
    formValues.accessibility,
    '`formValues.accessibility` is undefined'
  )

  return trimStringsInObject({
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues, isOfferArtistsFeatureActive),
    audioDisabilityCompliant: formValues.accessibility.audio,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    visualDisabilityCompliant: formValues.accessibility.visual,
    artistOfferLinks: serializeArtistOfferLinks(formValues.artistOfferLinks),
  })
}
