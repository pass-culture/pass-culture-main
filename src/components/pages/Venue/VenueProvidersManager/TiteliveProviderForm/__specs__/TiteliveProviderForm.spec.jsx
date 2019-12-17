import React from 'react'
import { mount, shallow } from 'enzyme'

import TiteliveProviderForm from '../TiteliveProviderForm'
import TextField from '../../../../../layout/form/fields/TextField'
import Icon from '../../../../../layout/Icon'
import { Form } from 'react-final-form'

describe('src | components | pages | Venue | VenueProvidersManager | form | TiteliveProviderForm', () => {
  let createVenueProvider
  let props
  let notify
  let history

  beforeEach(() => {
    createVenueProvider = jest.fn()
    history = {
      push: jest.fn(),
    }
    notify = jest.fn()
    props = {
      createVenueProvider,
      history,
      notify,
      offererId: 'CC',
      providerId: 'CC',
      venueId: 'AA',
      venueIdAtOfferProviderIsRequired: false,
    }
  })

  it('should initialize TiteliveProviderForm component with default state', () => {
    // when
    const wrapper = shallow(<TiteliveProviderForm {...props} />)

    // then
    expect(wrapper.state()).toStrictEqual({
      isLoadingMode: false,
    })
  })

  describe('when not in loading mode', () => {
    it('should display an import button', () => {
      // when
      const wrapper = mount(<TiteliveProviderForm {...props} />)

      // then
      const importButtonContainer = wrapper.find('.provider-import-button-container')
      expect(importButtonContainer).toHaveLength(1)
      const importButton = importButtonContainer.find('button')
      expect(importButton).toHaveLength(1)
      expect(importButton.prop('className')).toBe('button is-intermediate provider-import-button')
      expect(importButton.prop('type')).toBe('submit')
      expect(importButton.text()).toBe('Importer')
    })

    describe('when provider identifier is required', () => {
      it('should render a TextField component not in read only mode', () => {
        // given
        props.venueIdAtOfferProviderIsRequired = true

        // when
        const wrapper = mount(<TiteliveProviderForm {...props} />)

        // then
        const form = wrapper.find(Form)
        expect(form).toHaveLength(1)
        const label = form.find('label')
        expect(label.text()).toBe('Compte')
        const textField = form.find(TextField)
        expect(textField).toHaveLength(1)
        expect(textField.prop('className')).toBe('field-text')
        expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
        expect(textField.prop('readOnly')).toBe(false)
        expect(textField.prop('required')).toBe(true)
      })

      it('should display a tooltip and an Icon component', () => {
        // given
        props.venueIdAtOfferProviderIsRequired = true

        // when
        const wrapper = mount(<TiteliveProviderForm {...props} />)

        // then
        const tooltip = wrapper.find('.tooltip-info')
        expect(tooltip).toHaveLength(1)
        expect(tooltip.prop('className')).toBe('tooltip tooltip-info')
        expect(tooltip.prop('data-place')).toBe('bottom')
        expect(tooltip.prop('data-tip')).toBe('<p>Veuillez saisir un compte.</p>')
        const icon = tooltip.find(Icon)
        expect(icon).toHaveLength(1)
        expect(icon.prop('svg')).toBe('picto-info')
        expect(icon.prop('alt')).toBe('image d’aide à l’information')
      })
    })

    describe('when provider identifier is not required', () => {
      it('should render a TextField component in read only mode', () => {
        // given
        props.venueIdAtOfferProviderIsRequired = false

        // when
        const wrapper = mount(<TiteliveProviderForm {...props} />)

        // then
        const form = wrapper.find(Form)
        expect(form).toHaveLength(1)
        const label = form.find('label')
        expect(label.text()).toBe('Compte')
        const textField = form.find(TextField)
        expect(textField).toHaveLength(1)
        expect(textField.prop('className')).toBe('field-text field-is-read-only')
        expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
        expect(textField.prop('readOnly')).toBe(true)
        expect(textField.prop('required')).toBe(true)
      })

      it('should not display a tooltip and an Icon component', () => {
        // given
        props.venueIdAtOfferProviderIsRequired = false

        // when
        const wrapper = mount(<TiteliveProviderForm {...props} />)

        // then
        const tooltip = wrapper.find('.tooltip-info')
        expect(tooltip).toHaveLength(0)
      })
    })
  })

  describe('handleSubmit', () => {
    it('should update venue provider using API', () => {
      // given
      const formValues = {
        venueIdAtOfferProvider: 'token',
        preventDefault: jest.fn(),
      }
      const wrapper = shallow(<TiteliveProviderForm {...props} />)

      // when
      wrapper.instance().handleFormSubmit(formValues, {})

      // then
      expect(wrapper.state('isLoadingMode')).toBe(true)
      expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
        providerId: 'CC',
        venueId: 'AA',
        venueIdAtOfferProvider: 'token',
      })
    })
  })

  describe('handleSuccess', () => {
    it('should update current url when action was handled successfully', () => {
      // given
      const wrapper = shallow(<TiteliveProviderForm {...props} />)

      // when
      wrapper.instance().handleSuccess()

      // then
      expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/AA')
    })
  })

  describe('handleFail', () => {
    it('should display a notification with the proper informations', () => {
      // given
      const wrapper = shallow(<TiteliveProviderForm {...props} />)
      const action = {
        payload: {
          errors: [
            {
              error: 'fake error',
            },
          ],
        },
      }
      const form = {
        batch: jest.fn(),
      }
      // when
      wrapper.instance().handleFail(form)({}, action)
      // then
      expect(notify).toHaveBeenCalledWith([{ error: 'fake error' }])
    })
  })
})
