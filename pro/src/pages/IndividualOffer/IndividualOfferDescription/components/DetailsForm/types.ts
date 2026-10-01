import type { ArtistOfferLinkResponseModel } from '@/apiClient/v1'
import type { AccessibilityFormValues } from '@/commons/core/shared/types'

// TODO (igabriele, 2025-07-24): Make this type stricter (regarding optionals & null vs undefined).
export type DetailsFormValues = {
  name: string
  description?: string
  venueId: string
  categoryId: string
  hasCulturalOutreachClaim?: boolean
  subcategoryId: string
  showType?: string
  showSubType?: string
  gtl_id?: string
  author?: string
  artistOfferLinks: Array<ArtistOfferLinkResponseModel>
  performer?: string
  ean?: string
  eanSearch?: string
  speaker?: string
  stageDirector?: string
  visa?: string
  durationMinutes?: string | null
  subcategoryConditionalFields: (keyof DetailsFormValues)[]
  productId?: string
  callId?: string
  accessibility?: AccessibilityFormValues
}
