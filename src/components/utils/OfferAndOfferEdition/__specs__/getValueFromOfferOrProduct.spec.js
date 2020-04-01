import { getValueFromOfferOrProduct } from '../getValueFromOfferOrProduct'

describe('src | components | pages | Offer | utils | getValueFromOfferOrProduct', () => {
  it('should take info from product when creating a new offer from existing product', () => {
    // given
    const offer = {}
    const product = {
      description: 'PNL n’est plus ce qu’iel était',
    }

    // when
    const value = getValueFromOfferOrProduct('description', offer, product)

    // then
    expect(value).toStrictEqual(product.description)
  })

  it('should take information from offer when updating an offer', () => {
    // given
    const offer = {
      description: '',
      id: 'AE',
    }
    const product = {
      description: 'PNL n’est plus ce qu’il.elle était',
    }

    // when
    const value = getValueFromOfferOrProduct('description', offer, product)

    // then
    expect(value).toStrictEqual(offer.description)
  })
})
