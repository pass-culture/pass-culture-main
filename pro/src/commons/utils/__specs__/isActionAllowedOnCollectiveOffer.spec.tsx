import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'

import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '../collectiveApiFactories'
import { isActionAllowedOnCollectiveOffer } from '../isActionAllowedOnCollectiveOffer'

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
