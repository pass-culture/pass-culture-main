import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'

import { createCollectiveOfferPayload } from '../createOfferPayload'

describe('createOfferPayload', () => {
  it('should remove dates from a template offer to create a non-template offer', () => {
    expect(
      createCollectiveOfferPayload(
        {
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: '2021-09-01',
          endingDate: '2021-09-10',
        },
        false
      )
    ).toEqual(expect.objectContaining({ dates: undefined }))
  })

  it('should not remove dates from an offer to create a template offer', () => {
    expect(
      createCollectiveOfferPayload(
        {
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: '2021-09-01',
          endingDate: '2021-09-10',
          datesType: 'specific_dates',
        },
        true
      ).dates
    ).toBeTruthy()
  })

  it('should remove dates from an offer that has no valid dates to create a template offer', () => {
    expect(
      createCollectiveOfferPayload(
        {
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: undefined,
          endingDate: undefined,
        },
        true
      )
    ).toEqual(expect.objectContaining({ dates: undefined }))
  })
})
