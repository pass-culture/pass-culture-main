import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'

import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '../factories/collectiveApiFactories'
import {
  isActionAllowedOnCollectiveOffer,
  isCollectiveOfferDetailsEditable,
  isCollectiveOfferEditable,
  isCollectiveOfferSelectable,
} from '../isActionAllowedOnCollectiveOffer'

describe('isActionAllowedOnCollectiveOffer', () => {
  it.each([
    {
      description: 'allowed action CAN_DUPLICATE on bookable offer ',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
      }),
      action: CollectiveOfferAllowedAction.CAN_DUPLICATE,
      expected: true,
    },
    {
      description: 'allowed action CAN_CREATE_BOOKABLE_OFFER on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
        isTemplate: true,
      }),
      action: CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      expected: true,
    },
    {
      description: 'not allowed action CAN_DUPLICATE on bookable offer ',
      offer: getCollectiveOfferFactory({
        allowedActions: [],
      }),
      action: CollectiveOfferAllowedAction.CAN_DUPLICATE,
      expected: false,
    },
    {
      description:
        'not allowed action CAN_CREATE_BOOKABLE_OFFER on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [],
        isTemplate: true,
      }),
      action: CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      expected: false,
    },
  ])(
    'should return $expected for $description',
    ({ offer, action, expected }) => {
      expect(isActionAllowedOnCollectiveOffer(offer, action)).toBe(expected)
    }
  )
})

describe('isCollectiveOfferDetailsEditable', () => {
  it.each([
    {
      description:
        'should be editable when CAN_EDIT_DETAILS is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      }),
      expected: true,
    },
    {
      description:
        'should be editable when CAN_EDIT_DETAILS is allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
        isTemplate: true,
      }),
      expected: true,
    },
    {
      description:
        'should not be editable when no relevant actions are allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
      expected: false,
    },
    {
      description:
        'should not be editable when no relevant actions are allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
        isTemplate: true,
      }),
      expected: false,
    },
    {
      description: 'should not be editable when no actions are allowed',
      offer: getCollectiveOfferFactory({
        allowedActions: [],
      }),
      expected: false,
    },
  ])('$description', ({ offer, expected }) => {
    expect(isCollectiveOfferDetailsEditable(offer)).toBe(expected)
  })
})

describe('isCollectiveOfferSelectable', () => {
  it.each([
    {
      description:
        'should be selectable when CAN_ARCHIVE is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
      expected: true,
    },
    {
      description:
        'should be selectable when CAN_ARCHIVE is allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
        isTemplate: true,
      }),
      expected: true,
    },
    {
      description:
        'should be selectable when CAN_PUBLISH is allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
        isTemplate: true,
      }),
      expected: true,
    },
    {
      description:
        'should be selectable when CAN_HIDE is allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
        isTemplate: true,
      }),
      expected: true,
    },
    {
      description:
        'should not be selectable when no relevant actions are allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
      }),
      expected: false,
    },
    {
      description:
        'should not be selectable when no relevant actions are allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE],
        isTemplate: true,
      }),
      expected: false,
    },
    {
      description: 'should not be selectable when no actions are allowed',
      offer: getCollectiveOfferFactory({
        allowedActions: [],
      }),
      expected: false,
    },
  ])('$description', ({ offer, expected }) => {
    expect(isCollectiveOfferSelectable(offer)).toBe(expected)
  })
})

describe('isCollectiveOfferEditable', () => {
  it.each([
    {
      description:
        'should be editable when CAN_EDIT_DETAILS is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      }),
      expected: true,
    },
    {
      description:
        'should be editable when CAN_EDIT_DATES is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DATES],
      }),
      expected: true,
    },
    {
      description:
        'should be editable when CAN_EDIT_INSTITUTION is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION],
      }),
      expected: true,
    },
    {
      description:
        'should be editable when CAN_EDIT_DISCOUNT is allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT],
      }),
      expected: true,
    },
    {
      description:
        'should be editable when CAN_EDIT_DETAILS is allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
      }),
      expected: true,
    },
    {
      description:
        'should not be editable when no relevant actions are allowed on bookable offer',
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
      expected: false,
    },
    {
      description:
        'should not be editable when no relevant actions are allowed on template offer',
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
        isTemplate: true,
      }),
      expected: false,
    },
  ])('$description', ({ offer, expected }) => {
    expect(isCollectiveOfferEditable(offer)).toBe(expected)
  })
})
