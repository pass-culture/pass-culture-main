export const CollectiveOfferStep = {
  DETAILS: 'DETAILS',
  STOCKS: 'STOCKS',
  INSTITUTION: 'INSTITUTION',
  SUMMARY: 'SUMMARY',
  PREVIEW: 'PREVIEW',
  CONFIRMATION: 'CONFIRMATION',
} as const

export type CollectiveOfferStep = keyof typeof CollectiveOfferStep
