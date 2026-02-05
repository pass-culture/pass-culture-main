import { ArtistType } from '@/apiClient/v1'

// TODO (igabriele, 2025-07-24): Either remove useless initialized props or make them strict and non-optional once the FF is enabled in production.
export const DEFAULT_DETAILS_FORM_VALUES = {
  name: '',
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
      artistId: null,
      artistName: '',
      artistType: ArtistType.AUTHOR,
    },
    {
      artistId: null,
      artistName: '',
      artistType: ArtistType.PERFORMER,
    },
    {
      artistId: null,
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
