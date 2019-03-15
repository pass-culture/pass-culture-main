import React from 'react'
import { shallow } from 'enzyme'
import { Field } from 'pass-culture-shared'
import DateTimeForm from '../DateTimeForm'

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | DateTimeForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {}

      // when
      const wrapper = shallow(<DateTimeForm {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('functions', () => {
    describe('handleEventOccurrenceSuccessData', () => {
      it('should push correct url to history to permit to patch form', () => {
        // given
        const state = {}
        const action = {
          config: {},
          payload: {
            datum: {
              id: 'K9',
            },
          },
          type: 'SUCCESS_DATA_PATCH_EVENTOCCURRENCES/K9',
        }
        const historyMock = { push: jest.fn() }
        const initialProps = {
          history: historyMock,
          offer: {
            id: 'TY',
          },
          stockPatch: {
            id: 'DG',
          },
        }

        // when
        const wrapper = shallow(<DateTimeForm {...initialProps} />)
        wrapper.instance().handleEventOccurrenceSuccessData(state, action)
        const expected = '/offres/TY?gestion&date=K9&stock=DG'

        // then
        expect(historyMock.push).toHaveBeenCalledWith(expected)
      })
    })

    describe('render', () => {
      describe('highlightedDates', () => {
        it('TITUDYDSTISDKW', () => {
          // given
          const historyMock = { push: jest.fn() }
          const initialProps = {
            beginningDatetime: '2019-03-30T14:58:26Z',
            history: historyMock,
            offer: {
              id: 'TY',
            },
            stockPatch: {
              id: 'DG',
            },
            eventOccurrences: [
              {
                beginningDatetime: '2019-03-30T14:58:26Z',
              },
              {
                beginningDatetime: '2019-04-01T17:39:26Z',
              },
            ],
          }

          // when
          const wrapper = shallow(<DateTimeForm {...initialProps} />)
          const field = wrapper.find(Field)
          const quantityField = field.at(3)
          const expected = ['2019-03-30T14:58:26Z', '2019-04-01T17:39:26Z']

          // then
          expect(quantityField.props().highlightedDates).toEqual(expected)
        })
      })
    })
  })
})
