import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import { requestData } from 'redux-saga-data'
import BookingContainer from '../../../booking/BookingContainer'
import { recommendationNormalizer } from '../../../../utils/normalizers'
import { SearchDetails } from '../SearchDetails'
import RectoContainer from '../../../recto/RectoContainer'
import VersoContainer from '../../../verso/VersoContainer'

describe('src | components | pages | search | SearchDetails', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      dispatch: fakeMethod,
      match: {
        params: {
          mediationId: 'DU',
          offerId: 'EA',
          option: 'Applaudir',
        },
      },
      recommendation: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<SearchDetails {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleRequestData()', () => {
    it('should dispatch the request data', () => {
      // when
      const wrapper = shallow(<SearchDetails {...props} />)
      wrapper.instance().handleRequestData()
      const expectedData = requestData({
        apiPath: `/recommendations/offers/${props.match.params.offerId}`,
        handleSuccess: wrapper.instance().handleForceDetailsVisible,
        normalizer: recommendationNormalizer,
        stateKeys: 'searchRecommendations',
      })

      // then
      expect(props.dispatch).toHaveBeenCalledWith(expectedData)
      props.dispatch.mockClear()
    })
  })

  describe('handleForceDetailsVisible()', () => {
    it('should set forceDetailsVisible to true', () => {
      // when
      const wrapper = shallow(<SearchDetails {...props} />)
      wrapper.instance().handleForceDetailsVisible()

      // then
      expect(wrapper.state(['forceDetailsVisible'])).toBe(true)
    })
  })

  describe('render()', () => {
    it('should have one BookingContainer', () => {
      // given
      const state = { forceDetailsVisible: true }
      const routeProps = {
        path:
          '/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/(booking|cancelled)/:bookingId?',
      }

      // when
      const wrapper = shallow(<SearchDetails {...props} />)

      // then
      expect(wrapper.find(Route)).toHaveLength(0)
      wrapper.setState(state)
      const route = wrapper.find(routeProps)
      const renderRoute = route.props()
      expect(renderRoute.render().type).toBe(BookingContainer)
    })

    it('should have no RectoContainer and VersoContainer', () => {
      // given
      props.recommendation = null

      // when
      const wrapper = shallow(<SearchDetails {...props} />)
      const rectoContainer = wrapper.find(RectoContainer)
      const versoContainer = wrapper.find(VersoContainer)

      // then
      expect(rectoContainer).toHaveLength(0)
      expect(versoContainer).toHaveLength(0)
    })

    it('should have one RectoContainer and one VersoContainer', () => {
      // when
      const wrapper = shallow(<SearchDetails {...props} />)
      const rectoContainer = wrapper.find(RectoContainer)
      const versoContainer = wrapper.find(VersoContainer)

      // then
      expect(rectoContainer).toHaveLength(1)
      expect(versoContainer).toHaveLength(1)
    })
  })
})
