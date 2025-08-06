import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { itShouldReturnFalseIfGivenUndefinedOrNull } from '@/commons/utils/types'

import { isCollectiveOffer, isCollectiveOfferTemplate } from '../types'

describe('isCollectiveOffer', () => {
  itShouldReturnFalseIfGivenUndefinedOrNull(isCollectiveOffer)

  it('should return true if the object is a collective offer', () => {
    expect(isCollectiveOffer(getCollectiveOfferFactory())).toBe(true)
  })

  it('should return false if the object is not a collective offer', () => {
    expect(isCollectiveOffer({ someProp: 'test' })).toBe(false)
    expect(isCollectiveOffer(getCollectiveOfferTemplateFactory())).toBe(false)
  })
})

describe('isCollectiveOfferTemplate', () => {
  itShouldReturnFalseIfGivenUndefinedOrNull(isCollectiveOfferTemplate)

  it('should return true if the object is a collective offer template', () => {
    expect(isCollectiveOfferTemplate(getCollectiveOfferTemplateFactory())).toBe(
      true
    )
  })

  it('should return false if the object is not a collective offer template', () => {
    expect(isCollectiveOfferTemplate({ someProp: 'test' })).toBe(false)
    expect(isCollectiveOfferTemplate(getCollectiveOfferFactory())).toBe(false)
  })
})
