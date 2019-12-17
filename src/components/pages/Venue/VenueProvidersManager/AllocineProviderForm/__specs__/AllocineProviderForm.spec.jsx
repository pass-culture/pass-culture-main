import React from 'react'
import { mount, shallow } from 'enzyme'

import { Form } from 'react-final-form'
import TextField from '../../../../../layout/form/fields/TextField'
import NumberField from '../../../../../layout/form/fields/NumberField'
import Icon from '../../../../../layout/Icon'

import AllocineProviderForm from '../../AllocineProviderForm/AllocineProviderForm'
import SynchronisationConfirmationModal from '../SynchronisationConfirmationModal/SynchronisationConfirmationModal'

describe('src | components | pages | Venue | VenueProvidersManager | form | AllocineProviderForm', () => {
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
      providerId: 'AA',
      venueId: 'BB',
      venueIdAtOfferProviderIsRequired: false,
    }
  })

  it('should initialize AllocineProviderForm component with default state', () => {
    // when
    const wrapper = shallow(<AllocineProviderForm {...props} />)

    // then
    expect(wrapper.state()).toStrictEqual({
      isLoadingMode: false,
      isShowingConfirmationModal: false,
    })
  })

  it('should display an import button', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const importButtonContainer = wrapper.find('.provider-import-button-container')
    expect(importButtonContainer).toHaveLength(1)
    const importButton = importButtonContainer.find('button')
    expect(importButton).toHaveLength(1)
    expect(importButton.prop('className')).toBe('button is-intermediate provider-import-button')
    expect(importButton.prop('type')).toBe('button')
    expect(importButton.text()).toBe('Importer')
  })

  it('should display the price field', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceSection = wrapper.find(Form).find('.price-section')
    expect(priceSection).toHaveLength(1)
    const label = priceSection.find('label')
    expect(label.text()).toBe('Prix de vente/place')
    const priceInput = priceSection.find(NumberField)
    expect(priceInput).toHaveLength(1)
  })

  it('should display a tooltip and an Icon component for price field', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceSection = wrapper.find(Form).find('.price-section')
    const tooltip = priceSection.find('.tooltip-info')
    expect(tooltip).toHaveLength(1)
    expect(tooltip.prop('className')).toBe('tooltip tooltip-info')
    expect(tooltip.prop('data-place')).toBe('bottom')
    expect(tooltip.prop('data-tip')).toBe(
      '<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue</p>'
    )
    const icon = tooltip.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('picto-info')
    expect(icon.prop('alt')).toBe('image d’aide à l’information')
  })

  describe('when provider identifier is required', () => {
    it('should render a account field not in read only mode', () => {
      // given
      props.venueIdAtOfferProviderIsRequired = true

      // when
      const wrapper = mount(<AllocineProviderForm {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(1)
      const label = form.find('label[htmlFor="venueIdAtOfferProvider"]')
      expect(label.text()).toBe('Compte')
      const textField = form.find('.compte-section').find(TextField)
      expect(textField).toHaveLength(1)
      expect(textField.prop('className')).toBe('field-text')
      expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
      expect(textField.prop('readOnly')).toBe(false)
      expect(textField.prop('required')).toBe(true)
    })

    it('should display a tooltip and an Icon component for account field', () => {
      // given
      props.isLoadingMode = false
      props.venueIdAtOfferProviderIsRequired = true

      // when
      const wrapper = mount(<AllocineProviderForm {...props} />)

      // then
      const tooltip = wrapper.find('#compte-tooltip')
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
    it('should render a account field in read only mode', () => {
      // given
      props.isLoadingMode = true
      props.venueIdAtOfferProviderIsRequired = false

      // when
      const wrapper = mount(<AllocineProviderForm {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(1)
      const label = form.find('label[htmlFor="venueIdAtOfferProvider"]')
      expect(label.text()).toBe('Compte')
      const textField = form.find('.compte-section').find(TextField)
      expect(textField).toHaveLength(1)
      expect(textField.prop('className')).toBe('field-text field-is-read-only')
      expect(textField.prop('name')).toBe('venueIdAtOfferProvider')
      expect(textField.prop('readOnly')).toBe(true)
      expect(textField.prop('required')).toBe(true)
    })

    it('should not display a tooltip and an Icon component for account field', () => {
      // given
      props.isLoadingMode = false
      props.venueIdAtOfferProviderIsRequired = false

      // when
      const wrapper = mount(<AllocineProviderForm {...props} />)

      // then
      const tooltip = wrapper.find('.compte-section').find('.tooltip-info')
      expect(tooltip).toHaveLength(0)
    })
  })

  describe('when the import is clicked', () => {
    it('should display a synchronisation modal', () => {
      // given
      const wrapper = mount(<AllocineProviderForm {...props} />)

      // when
      wrapper.find('.provider-import-button').simulate('click')

      // then
      const synchronisationModal = wrapper.find(SynchronisationConfirmationModal)
      expect(synchronisationModal).toHaveLength(1)
    })
  })

  describe('handleSuccess', () => {
    it('should update current url when action was handled successfully', () => {
      // given
      const wrapper = shallow(<AllocineProviderForm {...props} />)

      // when
      wrapper.instance().handleSuccess()

      // then
      expect(history.push).toHaveBeenCalledWith('/structures/CC/lieux/BB')
    })
  })

  describe('handleFail', () => {
    it('should display a notification with the proper informations', () => {
      // given
      const wrapper = shallow(<AllocineProviderForm {...props} />)
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

  describe('handleSubmit', () => {
    it('should update venue provider using API', () => {
      // given
      const formValues = {
        price: 12,
        venueIdAtOfferProvider: 'token',
      }
      const wrapper = shallow(<AllocineProviderForm {...props} />)

      // when
      wrapper.instance().handleSubmit(formValues, {})

      // then
      expect(wrapper.state('isLoadingMode')).toBe(true)
      expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
        price: 12,
        providerId: 'AA',
        venueId: 'BB',
        venueIdAtOfferProvider: 'token',
      })
    })
  })
})
