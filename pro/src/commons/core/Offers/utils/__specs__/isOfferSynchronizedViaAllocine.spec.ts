import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { isOfferSynchronizedViaAllocine } from '../isOfferSynchronizedViaAllocine'

describe('isOfferSynchronizedViaAllocine', () => {
  it('should return true if last provider name is Allociné', () => {
    expect(
      isOfferSynchronizedViaAllocine(
        getIndividualOfferFactory({
          lastProvider: {
            name: 'Allociné',
          },
        })
      )
    ).toBe(true)
  })

  it('should return false if last provider name does not contain Allociné', () => {
    expect(
      isOfferSynchronizedViaAllocine(
        getIndividualOfferFactory({
          lastProvider: {
            name: 'Anyotherprovider',
          },
        })
      )
    ).toBe(false)
  })

  it('should return false if last provider is null', () => {
    expect(
      isOfferSynchronizedViaAllocine(
        getIndividualOfferFactory({
          lastProvider: null,
        })
      )
    ).toBe(false)
  })

  it('should return false if last provider is undefined', () => {
    expect(
      isOfferSynchronizedViaAllocine(
        getIndividualOfferFactory({ lastProvider: undefined })
      )
    ).toBe(false)
  })
})
