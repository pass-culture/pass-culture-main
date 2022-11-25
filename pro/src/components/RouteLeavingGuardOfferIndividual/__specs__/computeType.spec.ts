import { OFFER_WIZARD_MODE } from 'core/Offers'

import {
  computeType,
  ROUTE_LEAVING_GUARD_TYPE,
} from '../RouteLeavingGuardOfferIndividual'

describe('computeType', () => {
  // hasOfferBeenCreated does not matter here
  const edition = [
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isFormValid: true,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isFormValid: false,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isFormValid: false,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DEFAULT,
    },
    {
      mode: OFFER_WIZARD_MODE.EDITION,
      isFormValid: true,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.EDITION,
    },
  ]

  it.each(edition)('should return right type in edition', async param => {
    // Given
    const mode = param.mode
    const isFormValid = param.isFormValid
    const hasOfferBeenCreated = param.hasOfferBeenCreated
    const isInsideOfferJourney = param.isInsideOfferJourney

    // When
    const result = computeType(
      mode,
      isFormValid,
      hasOfferBeenCreated,
      isInsideOfferJourney
    )

    // Then
    expect(result).toStrictEqual(param.expected)
  })

  // hasOfferBeenCreated does not matter here
  const draft = [
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isFormValid: true,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isFormValid: false,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isFormValid: false,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DEFAULT,
    },
    {
      mode: OFFER_WIZARD_MODE.DRAFT,
      isFormValid: true,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DRAFT,
    },
  ]
  it.each(draft)('should return right type in draft', async param => {
    // Given
    const mode = param.mode
    const isFormValid = param.isFormValid
    const hasOfferBeenCreated = param.hasOfferBeenCreated
    const isInsideOfferJourney = param.isInsideOfferJourney

    // When
    const result = computeType(
      mode,
      isFormValid,
      hasOfferBeenCreated,
      isInsideOfferJourney
    )

    // Then
    expect(result).toStrictEqual(param.expected)
  })

  // hasOfferBeenCreated is false
  const creationBeforeOffer = [
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: true,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: false,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: false,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DEFAULT,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: true,
      hasOfferBeenCreated: false,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.CAN_CREATE_DRAFT,
    },
  ]
  it.each(creationBeforeOffer)(
    'should return right type in creation before offer exist',
    async param => {
      // Given
      const mode = param.mode
      const isFormValid = param.isFormValid
      const hasOfferBeenCreated = param.hasOfferBeenCreated
      const isInsideOfferJourney = param.isInsideOfferJourney

      // When
      const result = computeType(
        mode,
        isFormValid,
        hasOfferBeenCreated,
        isInsideOfferJourney
      )

      // Then
      expect(result).toStrictEqual(param.expected)
    }
  )

  // hasOfferBeenCreated is true
  const creationAftereOffer = [
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: true,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: false,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: true,
      expected: ROUTE_LEAVING_GUARD_TYPE.INTERNAL_NOT_VALID,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: false,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DEFAULT,
    },
    {
      mode: OFFER_WIZARD_MODE.CREATION,
      isFormValid: true,
      hasOfferBeenCreated: true,
      isInsideOfferJourney: false,
      expected: ROUTE_LEAVING_GUARD_TYPE.DRAFT,
    },
  ]
  it.each(creationAftereOffer)(
    'should return right type in creation after offer exist',
    async param => {
      // Given
      const mode = param.mode
      const isFormValid = param.isFormValid
      const hasOfferBeenCreated = param.hasOfferBeenCreated
      const isInsideOfferJourney = param.isInsideOfferJourney

      // When
      const result = computeType(
        mode,
        isFormValid,
        hasOfferBeenCreated,
        isInsideOfferJourney
      )

      // Then
      expect(result).toStrictEqual(param.expected)
    }
  )
})
