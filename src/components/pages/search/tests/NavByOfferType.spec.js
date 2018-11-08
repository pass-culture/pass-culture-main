import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import NavByOfferType from '../NavByOfferType'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | NavByOfferType', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {
        data: {
          types: [
            {
              description:
                'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
              id: 0,
              sublabel: 'Regarder',
            },
            {
              description: 'Lorem Ipsum',
              id: 1,
              sublabel: 'Rencontrer',
            },
          ],
        },
      }
      const store = mockStore(initialState)
      const props = {
        pagination: {},
        title: 'fake Title',
        typeSublabels: [],
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <NavByOfferType {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('functions', () => {
    describe('onClick', () => {
      describe('///////////// TODO TODO', () => {
        describe('///////////// TODO TODO', () => {
          it('should call change function with good parameters', () => {
            // given
            // when
            // then
          })
        })
      })
    })
  })
})
