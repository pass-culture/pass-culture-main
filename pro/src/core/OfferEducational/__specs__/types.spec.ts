import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { itShouldReturnFalseIfGivenUndefinedOrNull } from 'utils/types'

import { isCollectiveOffer, isCollectiveOfferTemplate } from '../types'

describe('isCollectiveOffer', () => {
  itShouldReturnFalseIfGivenUndefinedOrNull(isCollectiveOffer)

  it('should return true if the object is a collective offer', () => {
    expect(isCollectiveOffer(collectiveOfferFactory())).toBe(true)
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
    expect(isCollectiveOfferTemplate(collectiveOfferFactory())).toBe(false)
  })
})
