import type {
  ArtistOfferLinkBodyModelV2,
  ArtistOfferLinkResponseModelV2,
  FormatEnum,
  NatureEnum,
  PatchOfferBodyModel,
  PostNFDOfferBodyModel,
} from '@/apiClient/v1'
import { normalizeRequestBodyProps } from '@/commons/utils/normalizeRequestBodyProps'
import { trimStringsInObject } from '@/commons/utils/trimStringsInObject'
import { EXTRA_DATA_FORM_FIELDS } from '@/pages/IndividualOffer/IndividualOfferDescription/components/DetailsForm/constants'

import type { DescriptionFormValues } from './validationSchemaV2'

const serializeExtraData = (formValues: DescriptionFormValues) => {
  return normalizeRequestBodyProps({
    author: formValues.extraData?.author,
    gtl_id: formValues.extraData?.gtl_id,
    performer: formValues.extraData?.performer,
    showType: formValues.extraData?.showType,
    showSubType: formValues.extraData?.showSubType,
    speaker: formValues.extraData?.speaker,
    stageDirector: formValues.extraData?.stageDirector,
    visa: formValues.extraData?.visa,
    ean: formValues.extraData?.ean,
  })
}

const sanitizeArtistOfferLinks = (
  artistOfferLinks: ArtistOfferLinkResponseModelV2[]
): ArtistOfferLinkBodyModelV2[] => {
  return artistOfferLinks
    .filter((artist) => !!artist.artistName?.trim())
    .map((link) => ({
      artistId: link.artistId,
      artistName: link.artistName.trim(),
      artistType: link.artistType,
    }))
}

export function serializeDescriptionPostData(
  formValues: DescriptionFormValues,
  venueId: number,
  nature: NatureEnum,
  format: FormatEnum
): PostNFDOfferBodyModel {
  return trimStringsInObject({
    name: formValues.name ?? '',
    venueId: venueId,
    description: formValues.description ?? null,
    durationMinutes: formValues.durationMinutes,
    extraData: serializeExtraData(formValues),
    hasCulturalOutreachClaim: formValues.hasCulturalOutreachClaim ?? null,
    // TO assign when EAN is done for NFD
    productId: null,
    // TO assign when event nature is done for NFD
    audioDisabilityCompliant: false,
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: false,
    visualDisabilityCompliant: formValues.visualDisabilityCompliant ?? false,
    // @ts-expect-error - Waiting for pydanticV2 migration
    artistOfferLinks: sanitizeArtistOfferLinks(formValues.artistOfferLinks),
    nature: nature,
    format: format,
  })
}

export function serializeDescriptionPatchData(
  formValues: DescriptionFormValues,
  readOnlyFields: string[] = []
): PatchOfferBodyModel {
  const isReadOnly = (field: string) => readOnlyFields.includes(field)

  const shouldIncludeExtraData = EXTRA_DATA_FORM_FIELDS.some(
    (f) => !isReadOnly(f)
  )

  return trimStringsInObject({
    ...(!isReadOnly('name') && { name: formValues.name }),
    ...(!isReadOnly('description') && { description: formValues.description }),
    ...(!isReadOnly('durationMinutes') && {
      durationMinutes: formValues.durationMinutes,
    }),
    ...(shouldIncludeExtraData && {
      extraData: serializeExtraData(formValues),
    }),
    ...(!isReadOnly('hasCulturalOutreachClaim') && {
      hasCulturalOutreachClaim: formValues.hasCulturalOutreachClaim,
    }),
    ...(!isReadOnly('visualDisabilityCompliant') && {
      visualDisabilityCompliant: formValues.visualDisabilityCompliant,
    }),
    ...(!isReadOnly('artistOfferLinks') && {
      // @ts-expect-error - Waiting for pydanticV2 migration
      artistOfferLinks: sanitizeArtistOfferLinks(formValues.artistOfferLinks),
    }),
  })
}
