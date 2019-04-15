import React from 'react'
import { shallow } from 'enzyme'

import RawMediationsManager from '../RawMediationsManager'

describe('src | components | pages | Offer | MediationsManager | RawMediationsManager', () => {
  const dispatchMock = jest.fn()
  const offer = {
    bookingEmail: 'pctest.admin93.0@btmx.fr',
    dateCreated: '2019-03-26T14:59:19.832233Z',
    dateModifiedAtLastProvider: '2019-03-26T14:59:19.832208Z',
    eventId: null,
    id: 'N9',
    idAtProviders: null,
    isActive: true,
    lastProviderId: null,
    modelName: 'Offer',
    productId: '94',
    venueId: 'C4',
  }
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        dispatch: dispatchMock,
        mediations: [],
      }

      // when
      const wrapper = shallow(<RawMediationsManager {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
