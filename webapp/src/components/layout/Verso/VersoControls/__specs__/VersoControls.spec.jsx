import { shallow } from 'enzyme'
import React from 'react'

import ShareButtonContainer from '../../../Share/ShareButton/ShareButtonContainer'
import BookingActionContainer from '../booking/BookingAction/BookingActionContainer'
import CancellingActionContainer from '../booking/CancellingAction/CancellingActionContainer'
import FavoriteContainer from '../Favorite/FavoriteContainer'
import VersoControls from '../VersoControls'
import WalletContainer from '../Wallet/WalletContainer'

describe('src | components | VersoControls', () => {
  describe('when the offer is not booked', () => {
    it('should render the wallet, the favorite button, the share button and the booking link', () => {
      // given
      const props = {
        isBooked: false,
      }

      // when
      const wrapper = shallow(<VersoControls {...props} />)

      // then
      const walletContainer = wrapper.find(WalletContainer)
      const favoriteContainer = wrapper.find(FavoriteContainer)
      const shareButtonContainer = wrapper.find(ShareButtonContainer)
      const bookingActionContainer = wrapper.find(BookingActionContainer)
      expect(walletContainer).toHaveLength(1)
      expect(favoriteContainer).toHaveLength(1)
      expect(shareButtonContainer).toHaveLength(1)
      expect(bookingActionContainer).toHaveLength(1)
    })
  })

  describe('when the offer is booked', () => {
    it('should render the wallet, the favorite button, the share button and the cancelling link', () => {
      // given
      const props = {
        isBooked: true,
      }

      // when
      const wrapper = shallow(<VersoControls {...props} />)

      // then
      const walletContainer = wrapper.find(WalletContainer)
      const favoriteContainer = wrapper.find(FavoriteContainer)
      const shareButtonContainer = wrapper.find(ShareButtonContainer)
      const cancellingActionContainer = wrapper.find(CancellingActionContainer)
      expect(walletContainer).toHaveLength(1)
      expect(favoriteContainer).toHaveLength(1)
      expect(shareButtonContainer).toHaveLength(1)
      expect(cancellingActionContainer).toHaveLength(1)
    })
  })
})
