export const CollectiveOfferTemplateStep = {
  DETAILS: 'DETAILS',
  SUMMARY: 'SUMMARY',
  PREVIEW: 'PREVIEW',
  CONFIRMATION: 'CONFIRMATION',
} as const

export type CollectiveOfferTemplateStep =
  keyof typeof CollectiveOfferTemplateStep
