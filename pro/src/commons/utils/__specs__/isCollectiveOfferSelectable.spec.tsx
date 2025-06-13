import {
    CollectiveOfferAllowedAction,
    CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'

import {
    getCollectiveOfferFactory,
    getCollectiveOfferTemplateFactory,
} from '../factories/collectiveApiFactories'
import { isCollectiveOfferSelectable } from '../isCollectiveOfferSelectable'

describe('isCollectiveOfferSelectable', () => {
    it.each([
        {
            description: 'should be selectable when CAN_ARCHIVE is allowed on bookable offer',
            offer: getCollectiveOfferFactory({
                allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
            }),
            expected: true,
        },
        {
            description: 'should be selectable when CAN_ARCHIVE is allowed on template offer',
            offer: getCollectiveOfferTemplateFactory({
                allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
                isTemplate: true,
            }),
            expected: true,
        },
        {
            description: 'should be selectable when CAN_PUBLISH is allowed on template offer',
            offer: getCollectiveOfferTemplateFactory({
                allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
                isTemplate: true,
            }),
            expected: true,
        },
        {
            description: 'should be selectable when CAN_HIDE is allowed on template offer',
            offer: getCollectiveOfferTemplateFactory({
                allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
                isTemplate: true,
            }),
            expected: true,
        },
        {
            description: 'should not be selectable when no relevant actions are allowed on bookable offer',
            offer: getCollectiveOfferFactory({
                allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
            }),
            expected: false,
        },
        {
            description: 'should not be selectable when no relevant actions are allowed on template offer',
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
    ])(
        '$description',
        ({ offer, expected }) => {
            expect(isCollectiveOfferSelectable(offer)).toBe(expected)
        }
    )
}) 