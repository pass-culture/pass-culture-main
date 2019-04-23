import React from 'react'
import { shallow } from 'enzyme'

import RawMediationsManager from '../RawMediationsManager'

describe('src | components | pages | Offer | MediationsManager | RawMediationsManager', () => {
  const dispatchMock = jest.fn()
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
