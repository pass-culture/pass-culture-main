import { MOCKED_SUBCATEGORY } from '../__mocks__/constants'
import { getOfferConditionalFields } from '../getOfferConditionalFields'

describe('getOfferConditionalFields', () => {
  it('should return durationMinutes field when offer subcategory is an event', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.EVENT_OFFLINE,
      isEvent: true,
    }

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('durationMinutes')
  })

  it('should return isDuo field when offer subcategory can be duo', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE,
      canBeDuo: true,
    }

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('isDuo')
  })

  it('should return musicSubType field when offer subcategory has musicType conditional field', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE,
      conditionalFields: ['musicType'],
    }

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('musicSubType')
  })

  it('should return showSubType field when offer subcategory has showType conditional field', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE,
      conditionalFields: ['showType'],
    }

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('showSubType')
  })

  it('should return both musicSubType and showSubType when both conditional fields are present', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE,
      conditionalFields: ['musicType', 'showType'],
    }

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('musicSubType')
    expect(result).toContain('showSubType')
  })

  it('should return bookingEmail field when receiveNotificationEmails is true', () => {
    const offerSubcategory = MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE

    const result = getOfferConditionalFields({
      offerSubcategory,
      shouldReceiveEmailNotifications: true,
    })

    expect(result).toContain('bookingEmail')
  })

  it('should not return bookingEmail when receiveNotificationEmails is false', () => {
    const offerSubcategory = MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE

    const result = getOfferConditionalFields({
      offerSubcategory,
      shouldReceiveEmailNotifications: false,
    })

    expect(result).not.toContain('bookingEmail')
  })

  it('should return withdrawalType, withdrawalDelay and bookingContact fields when offer subcategory can be withdrawable', () => {
    const offerSubcategory = MOCKED_SUBCATEGORY.WIDTHDRAWABLE

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toContain('withdrawalType')
    expect(result).toContain('withdrawalDelay')
    expect(result).toContain('bookingContact')
  })

  it('should return all relevant fields with a combination of conditions', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE,
      isEvent: true,
      canBeDuo: true,
      conditionalFields: ['musicType'],
    }

    const result = getOfferConditionalFields({
      offerSubcategory,
      shouldReceiveEmailNotifications: true,
    })

    expect(result).toEqual([
      'durationMinutes',
      'isDuo',
      'musicSubType',
      'bookingEmail',
    ])
  })

  it('should return all fields in the expected order when all conditions are met including withdrawable', () => {
    const offerSubcategory = {
      ...MOCKED_SUBCATEGORY.WIDTHDRAWABLE,
      isEvent: true,
      canBeDuo: true,
      conditionalFields: ['musicType', 'showType'],
    }

    const result = getOfferConditionalFields({
      offerSubcategory,
      shouldReceiveEmailNotifications: true,
    })

    expect(result).toEqual([
      'durationMinutes',
      'isDuo',
      'musicSubType',
      'showSubType',
      'bookingEmail',
      'withdrawalType',
      'withdrawalDelay',
      'bookingContact',
    ])
  })

  it('should return an empty array when no conditions are met', () => {
    const offerSubcategory = MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE

    const result = getOfferConditionalFields({ offerSubcategory })

    expect(result).toEqual([])
  })
})
