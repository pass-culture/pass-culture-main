import { shallow } from 'enzyme'
import React from 'react'

import RectoContainer from '../../Recto/RectoContainer'
import VersoContainer from '../../Verso/VersoContainer'
import Details from '../Details'

describe('src | components | Details', () => {
  let props

  beforeEach(() => {
    props = {
      getOfferById: jest.fn(),
      match: {
        params: {},
      },
    }
  })

  describe('when I am not on the details of offer', () => {
    it('should display verso and not recto', () => {
      // when
      const wrapper = shallow(<Details {...props} />)

      // then
      const versoContainer = wrapper.find(VersoContainer)
      expect(versoContainer).toHaveLength(1)
      const rectoContainer = wrapper.find(RectoContainer)
      expect(rectoContainer).toHaveLength(0)
    })
  })

  describe('when I am on the details of offer', () => {
    it('should display verso and recto', () => {
      // given
      props.match.params.details = 'details'

      // when
      const wrapper = shallow(<Details {...props} />)

      // then
      const versoContainer = wrapper.find(VersoContainer)
      expect(versoContainer).toHaveLength(1)
      const rectoContainer = wrapper.find(RectoContainer)
      expect(rectoContainer).toHaveLength(1)
    })

    it('should fetch offers', () => {
      // given
      props.match.params.offerId = 'AE'

      // when
      shallow(<Details {...props} />)

      // then
      expect(props.getOfferById).toHaveBeenCalledWith('AE')
    })
  })
})
