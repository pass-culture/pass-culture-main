import { getProductById } from '../productsSelectors'

describe('src | selectors | data | productsSelectors', () => {
  describe('getProductById', () => {
    describe('when product exists in products', () => {
      it('should return it', () => {
        // given
        const store = {
          data: {
            products: [{
              id: 'AGKD',
            }]
          }
        }
        const productId = 'AGKD'

        // when
        const product = getProductById(store, productId)

        // then
        expect(product).toStrictEqual({
          id: 'AGKD'
        })
      })
    })
  })
})
