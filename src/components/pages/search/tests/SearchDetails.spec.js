import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../../../booking/BookingContainer'
import { recommendationNormalizer } from '../../../../utils/normalizers'
import { SearchDetails } from '../SearchDetails'
import RectoContainer from '../../../recto/RectoContainer'
import VersoContainer from '../../../verso/VersoContainer'

describe('src | components | pages | search | SearchDetails', () => {
  let props

  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      match: {
        params: {
          mediationId: 'DU',
          offerId: 'EA',
          option: 'Applaudir',
        },
      },
      recommendation: {
        id: 'EA',
      },
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
      // given
      const wrapper = shallow(<SearchDetails {...props} />)

      // when
      wrapper.instance().handleRequestData()

      // then
      expect(props.dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/recommendations/offers/${props.recommendation.id}`,
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: recommendationNormalizer,
          stateKeys: 'searchRecommendations',
        },
        type: `REQUEST_DATA_GET_/RECOMMENDATIONS/OFFERS/${
          props.recommendation.id
        }`,
      })
    })
  })

  describe('handleForceDetailsVisible()', () => {
    it('should force the details to be visible', () => {
      // given
      const wrapper = shallow(<SearchDetails {...props} />)

      // when
      wrapper.instance().handleForceDetailsVisible()

      // then
      expect(wrapper.state(['forceDetailsVisible'])).toBe(true)
    })
  })

  describe('render()', () => {
    it('should have one BookingContainer when I want details', () => {
      // given
      const state = { forceDetailsVisible: true }
      const routeProps = {
        path:
          '/recherche/resultats/:option?/item/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/(booking|cancelled)/:bookingId?',
      }
      const wrapper = shallow(<SearchDetails {...props} />)

      // then
      expect(wrapper.find(Route)).toHaveLength(0)
      wrapper.setState(state)
      const route = wrapper.find(routeProps)
      const renderRoute = route.props()
      expect(renderRoute.render().type).toBe(BookingContainer)
    })

    it('should have no RectoContainer and VersoContainer when there is no recommendation', () => {
      // given
      props.recommendation = null
      const wrapper = shallow(<SearchDetails {...props} />)

      // when
      const rectoContainer = wrapper.find(RectoContainer)
      const versoContainer = wrapper.find(VersoContainer)

      // then
      expect(rectoContainer).toHaveLength(0)
      expect(versoContainer).toHaveLength(0)
    })

    it('should have one RectoContainer and one VersoContainer by default', () => {
      // given
      const wrapper = shallow(<SearchDetails {...props} />)

      // when
      const rectoContainer = wrapper.find(RectoContainer)
      const versoContainer = wrapper.find(VersoContainer)

      // then
      expect(rectoContainer).toHaveLength(1)
      expect(versoContainer).toHaveLength(1)
    })
  })
})
