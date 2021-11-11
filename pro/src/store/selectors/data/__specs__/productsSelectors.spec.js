import { selectProductById } from '../productsSelectors'

describe('src | selectors | data | productsSelectors', () => {
  describe('selectProductById', () => {
    describe('when product exists in products', () => {
      it('should return it', () => {
        // given
        const store = {
          data: {
            products: [
              {
                id: 'AGKD',
              },
            ],
          },
        }
        const productId = 'AGKD'

        // when
        const product = selectProductById(store, productId)

        // then
        expect(product).toStrictEqual({
          id: 'AGKD',
        })
      })
    })

    describe('when product does not exist in products', () => {
      it('should return it', () => {
        // given
        const store = {
          data: {
            products: [],
          },
        }
        const productId = 'AGKD'

        // when
        const product = selectProductById(store, productId)

        // then
        expect(product).toStrictEqual()
      })
    })
  })
})
