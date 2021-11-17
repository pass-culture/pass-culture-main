import { shallow } from 'enzyme'
import React from 'react'
import { toast } from 'react-toastify'

import RectoContainer from '../../Recto/RectoContainer'
import VersoContainer from '../../Verso/VersoContainer'
import Details from '../Details'

jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

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

  describe('web app v2 redirection', () => {
    beforeEach(jest.useFakeTimers)
    afterEach(jest.clearAllTimers)

    it('should track and redirect to web app v2 home when offerId is missing', () => {
      // given
      const replace = jest.fn()
      const trackV1toV2HomeRedirect = jest.fn()
      const trackV1toV2OfferRedirect = jest.fn()
      jest.spyOn(window.location, 'replace').mockImplementation(replace)

      // when
      shallow(
        <Details
          {...props}
          trackV1toV2HomeRedirect={trackV1toV2HomeRedirect}
          trackV1toV2OfferRedirect={trackV1toV2OfferRedirect}
          webAppV2Enabled
        />
      )

      // then
      expect(trackV1toV2HomeRedirect).toHaveBeenCalledTimes(1)
      expect(trackV1toV2HomeRedirect).toHaveBeenCalledWith({
        offerId: undefined,
        url: 'http://localhost:3000',
      })
      expect(trackV1toV2OfferRedirect).not.toHaveBeenCalledTimes(1)
      jest.advanceTimersByTime(10000)
      expect(toast.error).toHaveBeenCalledWith(
        "Ce lien n'est plus à jour, tu vas être redirigé vers le nouveau site du pass Culture."
      )
      expect(replace).toHaveBeenCalledWith(process.env.WEBAPP_V2_URL)
    })

    it('should track and redirect to web app v2 home when offerId cannot be dehumanized', () => {
      // given
      props.match.params.offerId = '_'
      const replace = jest.fn()
      const trackV1toV2HomeRedirect = jest.fn()
      const trackV1toV2OfferRedirect = jest.fn()
      jest.spyOn(window.location, 'replace').mockImplementation(replace)

      // when
      shallow(
        <Details
          {...props}
          trackV1toV2HomeRedirect={trackV1toV2HomeRedirect}
          trackV1toV2OfferRedirect={trackV1toV2OfferRedirect}
          webAppV2Enabled
        />
      )

      // then
      expect(trackV1toV2HomeRedirect).toHaveBeenCalledTimes(1)
      expect(trackV1toV2HomeRedirect).toHaveBeenCalledWith({
        offerId: '_',
        url: 'http://localhost:3000',
      })
      expect(trackV1toV2OfferRedirect).not.toHaveBeenCalledTimes(1)
      jest.advanceTimersByTime(10000)
      expect(toast.error).toHaveBeenCalledWith(
        "Ce lien n'est plus à jour, tu vas être redirigé vers le nouveau site du pass Culture."
      )
      expect(replace).toHaveBeenCalledWith(process.env.WEBAPP_V2_URL)
    })

    it('should track and redirect to offer web app v2 home when offerId can be dehumanized', () => {
      // given
      props.match.params.offerId = 'BRXQ'
      const replace = jest.fn()
      const trackV1toV2HomeRedirect = jest.fn()
      const trackV1toV2OfferRedirect = jest.fn()
      jest.spyOn(window.location, 'replace').mockImplementation(replace)

      // when
      shallow(
        <Details
          {...props}
          trackV1toV2HomeRedirect={trackV1toV2HomeRedirect}
          trackV1toV2OfferRedirect={trackV1toV2OfferRedirect}
          webAppV2Enabled
        />
      )

      // then
      expect(trackV1toV2OfferRedirect).toHaveBeenCalledTimes(1)
      expect(trackV1toV2OfferRedirect).toHaveBeenCalledWith({
        offerId: 3183,
        url: 'http://localhost:3000/offre/3183',
      })
      expect(trackV1toV2HomeRedirect).not.toHaveBeenCalledTimes(1)
      jest.advanceTimersByTime(10000)
      expect(toast.error).toHaveBeenCalledWith(
        "Ce lien n'est plus à jour, tu vas être redirigé vers le nouveau site du pass Culture, pense à mettre à jour tes favoris."
      )
      expect(replace).toHaveBeenCalledWith(`${process.env.WEBAPP_V2_URL}/offre/3183`)
    })
  })
})
