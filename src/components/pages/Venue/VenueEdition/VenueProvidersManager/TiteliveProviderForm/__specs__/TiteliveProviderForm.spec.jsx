import { mount } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import TiteliveProviderForm from '../TiteliveProviderForm'

describe('src | TiteliveProviderForm', () => {
  let cancelProviderSelection
  let createVenueProvider
  let props
  let notify
  let history

  beforeEach(() => {
    cancelProviderSelection = jest.fn()
    createVenueProvider = jest.fn()
    history = {
      push: jest.fn(),
    }
    notify = jest.fn()
    props = {
      cancelProviderSelection,
      createVenueProvider,
      history,
      notify,
      offererId: 'CC',
      providerId: 'CC',
      venueId: 'AA',
      venueIdAtOfferProviderIsRequired: false,
      venueSiret: '12345678901234',
    }
  })

  describe('when not in loading mode', () => {
    it('should display an import button', () => {
      // when
      const wrapper = mount(<TiteliveProviderForm {...props} />)

      // then
      const importButton = wrapper.find({ children: 'Importer' })
      expect(importButton).toHaveLength(1)
      expect(importButton.prop('type')).toBe('submit')
    })

    it('should render the title of the section compte', () => {
      // when
      const wrapper = mount(<TiteliveProviderForm {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(1)
      const label = form.find({ children: 'Compte' })
      expect(label).toHaveLength(1)
    })

    it('should display the venue siret as provider identifier', () => {
      // when
      const wrapper = mount(<TiteliveProviderForm {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(1)
      const textField = form.find({ children: '12345678901234' })
      expect(textField).toHaveLength(1)
    })
  })

  describe('handleSubmit', () => {
    it('should update venue provider using API', () => {
      // given
      const wrapper = mount(<TiteliveProviderForm {...props} />)
      const payload = { providerId: 'CC', venueId: 'AA', venueIdAtOfferProvider: '12345678901234' }

      // when
      wrapper.find(Form).invoke('onSubmit')()

      // then
      expect(createVenueProvider).toHaveBeenCalledWith(
        expect.any(Function),
        expect.any(Function),
        payload
      )
    })
  })

  describe('handleSuccess', () => {
    it('should update current url when action was handled successfully', () => {
      // given
      const wrapper = mount(<TiteliveProviderForm {...props} />)
      createVenueProvider.mockImplementation((fail, success) => success())

      // when
      wrapper.find(Form).invoke('onSubmit')()

      // then
      expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/AA')
    })
  })

  describe('handleFail', () => {
    it('should display a notification with the proper informations', () => {
      // given
      const wrapper = mount(<TiteliveProviderForm {...props} />)
      const action = {
        payload: {
          errors: [
            {
              error: 'fake error',
            },
          ],
        },
      }
      createVenueProvider.mockImplementation(fail => fail(null, action))

      // when
      wrapper.find(Form).invoke('onSubmit')()

      // then
      expect(notify).toHaveBeenCalledWith([{ error: 'fake error' }])
      expect(cancelProviderSelection).toHaveBeenCalledTimes(1)
    })
  })
})
