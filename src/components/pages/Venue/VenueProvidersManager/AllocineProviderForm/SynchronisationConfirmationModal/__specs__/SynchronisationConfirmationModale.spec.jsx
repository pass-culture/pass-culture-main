import { shallow } from 'enzyme'
import React from 'react'

import SynchronisationConfirmationModal from '../SynchronisationConfirmationModal'

describe('src | components | pages | Venue | VenueProvidersManager | AllocineProviderForm | SynchronisationConfirmationModal', () => {
  describe('render', () => {
    let handleClose
    let handleConfirm
    let props

    beforeEach(() => {
      handleClose = jest.fn()
      handleConfirm = jest.fn()
      props = {
        handleClose,
        handleConfirm,
      }
    })

    it('should display warning text, cancel button and confirm button', () => {
      // when
      const wrapper = shallow(<SynchronisationConfirmationModal {...props} />)

      // then
      const warningText = wrapper.find('.warning-text').text()
      expect(warningText).toBe(
        'Vous ne pourrez plus modifier le prix de vente après la synchronisation.'
      )
      const cancelButton = wrapper.find('.cancel-button')
      expect(cancelButton).toHaveLength(1)
      const confirmButton = wrapper.find('.confirm-button')
      expect(confirmButton).toHaveLength(1)
    })

    it('should call handleClose function when click on cancel button', () => {
      // when
      const wrapper = shallow(<SynchronisationConfirmationModal {...props} />)
      wrapper.find('.cancel-button').simulate('click')

      // then
      expect(handleClose).toHaveBeenCalledWith()
    })

    it('should call handleConfirm function when click on confirm button', () => {
      // when
      const wrapper = shallow(<SynchronisationConfirmationModal {...props} />)
      wrapper.find('.confirm-button').simulate('click')

      // then
      expect(handleConfirm).toHaveBeenCalledWith()
    })
  })
})
