export type DetailsFormValues = {
  name: string
  description: string
  venueId: string
  categoryId: string
  subcategoryId: string
  showType: string
  showSubType: string
  musicType?: string
  musicSubType?: string
  gtl_id?: string
  author?: string
  performer?: string
  ean?: string
  speaker?: string
  stageDirector?: string
  visa?: string
  durationMinutes?: string | null
  subcategoryConditionalFields: string[]
}
