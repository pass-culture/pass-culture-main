import {
  collectiveOfferTemplateFactory,
  offerFactory,
} from 'screens/OfferEducationalStock/__tests-utils__'
import { itShouldReturnFalseIfGivenUndefinedOrNull } from 'utils/types'

import { isCollectiveOffer, isCollectiveOfferTemplate } from '../types'

describe('isCollectiveOffer', () => {
  itShouldReturnFalseIfGivenUndefinedOrNull(isCollectiveOffer)

  it('should return true if the object is a collective offer', () => {
    expect(isCollectiveOffer(offerFactory())).toBe(true)
  })

  it('should return false if the object is not a collective offer', () => {
    expect(isCollectiveOffer({ someProp: 'test' })).toBe(false)
    expect(isCollectiveOffer(collectiveOfferTemplateFactory())).toBe(false)
  })
})

describe('isCollectiveOfferTemplate', () => {
  itShouldReturnFalseIfGivenUndefinedOrNull(isCollectiveOfferTemplate)

  it('should return true if the object is a collective offer template', () => {
    expect(isCollectiveOfferTemplate(collectiveOfferTemplateFactory())).toBe(
      true
    )
  })

  it('should return false if the object is not a collective offer template', () => {
    expect(isCollectiveOfferTemplate({ someProp: 'test' })).toBe(false)
    expect(isCollectiveOfferTemplate(offerFactory())).toBe(false)
  })
})
