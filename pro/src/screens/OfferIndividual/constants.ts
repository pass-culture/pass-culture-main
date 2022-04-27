export enum OFFER_FORM_STEP_IDS {
  INFORMATIONS = 'informations',
  STOCKS = 'stocks',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

export const fakeOffer = {
  id: 'AL4Q',
  status: 'ACTIVE',
  isActive: true,
  hasBookingLimitDatetimesPassed: false,
  isEducational: false,
  name: 'Test Offer',
  isEvent: false,
  venue: {
    name: 'Test venu',
    offererName: 'Test offerer',
    isVirtual: false,
  },
  stocks: [],
  isEditable: true,
}
