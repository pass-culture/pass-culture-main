import {
  GetIndividualOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'

export type DetailsFormValues = {
  name: string
  description?: string
  venueId: string
  categoryId: string
  subcategoryId: string
  showType?: string
  showSubType?: string
  gtl_id?: string
  author?: string
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
  url?: string | null
}

export type Product = {
  id: number
  name: string
  description?: string | null
  subcategoryId: string
  gtlId: string
  author: string
  performer: string
  images: {
    recto?: string
    verso?: string
  }
}

export type SetDefaultInitialValuesFromOfferProps = {
  offer: GetIndividualOfferResponseModel
  subcategories: SubcategoryResponseModel[]
}
