import {
    CollectiveOfferAllowedAction,
    CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'

import {
    getCollectiveOfferFactory,
    getCollectiveOfferTemplateFactory,
} from '../factories/collectiveApiFactories'
import { isCollectiveOfferEditable } from '../isCollectiveOfferEditable'

describe('isCollectiveOfferEditable', () => {
    it.each([
        {
            description: 'should be editable when CAN_EDIT_DETAILS is allowed on bookable offer',
            offer: getCollectiveOfferFactory({
                allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
            }),
            expected: true,
        },
        {
            description: 'should be editable when CAN_EDIT_DETAILS is allowed on template offer',
            offer: getCollectiveOfferTemplateFactory({
                allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
                isTemplate: true,
            }),
            expected: true,
        },
        {
            description: 'should not be editable when no relevant actions are allowed on bookable offer',
            offer: getCollectiveOfferFactory({
                allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
            }),
            expected: false,
        },
        {
            description: 'should not be editable when no relevant actions are allowed on template offer',
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
    ])(
        '$description',
        ({ offer, expected }) => {
            expect(isCollectiveOfferEditable(offer)).toBe(expected)
        }
    )
}) 