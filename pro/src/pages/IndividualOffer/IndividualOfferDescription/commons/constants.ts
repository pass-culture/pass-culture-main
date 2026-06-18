import { ArtistType } from '@/apiClient/v1'

import type { DetailsFormValues } from './types'

export const EXTRA_DATA_FORM_FIELDS = [
  'author',
  'gtl_id',
  'performer',
  'showType',
  'showSubType',
  'speaker',
  'stageDirector',
  'visa',
  'ean',
  'artistOfferLinks',
] as const satisfies ReadonlyArray<keyof DetailsFormValues>

// TODO (igabriele, 2025-07-24): Either remove useless initialized props or make them strict and non-optional once the FF is enabled in production.
export const DEFAULT_DETAILS_FORM_VALUES = {
  name: '',
  hasCulturalOutreachClaim: false,
  description: '',
  venueId: '',
  categoryId: '',
  subcategoryId: '',
  gtl_id: '',
  showType: '',
  showSubType: '',
  speaker: '',
  author: '',
  artistOfferLinks: [
    {
      artistId: undefined,
      artistName: '',
      artistType: ArtistType.AUTHOR,
    },
    {
      artistId: undefined,
      artistName: '',
      artistType: ArtistType.PERFORMER,
    },
    {
      artistId: undefined,
      artistName: '',
      artistType: ArtistType.STAGE_DIRECTOR,
    },
  ],
  visa: '',
  stageDirector: '',
  performer: '',
  ean: '',
  durationMinutes: '',
  subcategoryConditionalFields: [],
  productId: '',
}
