import { getValueFromOfferOrProduct } from '../getValueFromOfferOrProduct'

describe('src | components | pages | Offer | utils | getValueFromOfferOrProduct', () => {
  it('should take info from product when offer has no idea, ie isCreatedEntity', () => {
    // given
    const offer = {}
    const product = {
      description: "PNL n'est plus ce qu'il.elle était",
    }

    // when
    const value = getValueFromOfferOrProduct('description', offer, product)

    // then
    expect(value).toEqual(product.description)
  })

  it('should take info from offer when offer.id, ie isModifiedEntity', () => {
    // given
    const offer = {
      description: '',
      id: 'AE',
    }
    const product = {
      description: "PNL n'est plus ce qu'il.elle était",
    }

    // when
    const value = getValueFromOfferOrProduct('description', offer, product)

    // then
    expect(value).toEqual(offer.description)
  })
})
