export type DetailsFormValues = {
  name: string
  description?: string | null
  venueId: string
  categoryId: string
  subcategoryId: string
  showType: string
  showSubType: string
  gtl_id?: string
  author?: string
  performer?: string
  ean?: string
  eanSearch?: string
  speaker?: string
  stageDirector?: string
  visa?: string
  durationMinutes?: string | null
  subcategoryConditionalFields: string[]
  suggestedSubcategory: string
  productId: string
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
