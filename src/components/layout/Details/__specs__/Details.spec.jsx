import { shallow } from 'enzyme'
import React from 'react'

import Details from '../Details'
import RectoContainer from '../../Recto/RectoContainer'
import VersoContainer from '../../Verso/VersoContainer'

describe('src | components | layout | Details | Details', () => {
  let props

  beforeEach(() => {
    props = {
      bookingPath: 'fake/path',
      getOfferById: jest.fn(),
      match: {
        params: {},
      },
    }
  })

  describe('render', () => {
    describe('when I have no details', () => {
      it('should render VersoContainer and not RectoContainer', () => {
        // when
        const wrapper = shallow(<Details {...props} />)

        // then
        const versoContainer = wrapper.find(VersoContainer)
        expect(versoContainer).toHaveLength(1)
        const rectoContainer = wrapper.find(RectoContainer)
        expect(rectoContainer).toHaveLength(0)
      })
    })

    describe('when I have details', () => {
      it('should render VersoContainer and RectoContainer', () => {
        // given
        props.match.params.details = 'details'

        // when
        const wrapper = shallow(<Details {...props} />)
        wrapper.setState({ isDetailsView: true })

        // then
        const versoContainer = wrapper.find(VersoContainer)
        expect(versoContainer).toHaveLength(1)
        const rectoContainer = wrapper.find(RectoContainer)
        expect(rectoContainer).toHaveLength(1)
      })
    })

    it('should fetch offer using offer id when coming from search', () => {
      // given
      props.match = {
        params: {
          offerId: 'AE'
        },
        path: '/recherche-algolia/details/AE'
      }

      // when
      shallow(<Details {...props} />)

      // then
      expect(props.getOfferById).toHaveBeenCalledWith('AE')
    })

    it('should not fetch offer when not coming from search', () => {
      // given
      props.match = {
        params: {
          offerId: 'AE'
        },
        path: '/decouverte/details/AE'
      }

      // when
      shallow(<Details {...props} />)

      // then
      expect(props.getOfferById).not.toHaveBeenCalledWith()
    })
  })
})
