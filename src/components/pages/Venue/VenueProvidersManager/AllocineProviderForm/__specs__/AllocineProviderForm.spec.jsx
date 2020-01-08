import React from 'react'
import { mount, shallow } from 'enzyme'

import { Form } from 'react-final-form'
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
      isShowingConfirmationModal: false,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<AllocineProviderForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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

  it('should display the price field with minimum value set to 0', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceSection = wrapper.find(Form).find('.price-section')
    expect(priceSection).toHaveLength(1)
    const label = priceSection.find('label')
    expect(label.text()).toBe('Prix de vente/place *')
    const priceInput = priceSection.find(NumberField)
    expect(priceInput).toHaveLength(1)
    expect(priceInput.prop('min')).toBe('0')
  })

  it('should display a tooltip and an Icon component for price field', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceSection = wrapper.find(Form).find('.price-section')
    const tooltip = priceSection.find('#price-tooltip')
    expect(tooltip).toHaveLength(1)
    expect(tooltip.prop('data-place')).toBe('bottom')
    expect(tooltip.prop('data-tip')).toBe(
      '<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>'
    )
    const icon = tooltip.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('picto-info')
    expect(icon.prop('alt')).toBe('image d’aide à l’information')
  })

  it('should display a confirmation modal', () => {
    // given
    const wrapper = mount(<AllocineProviderForm {...props} />)
    const importButton = wrapper.find('button')
    const priceSection = wrapper.findWhere(node => node.text() === 'Prix de vente/place *')
    const priceInput = priceSection.find(NumberField).find('input')
    priceInput.simulate('change', { target: { value: 10 } })

    // when
    importButton.simulate('click')

    // then
    const syncConfirmationModal = wrapper.find(SynchronisationConfirmationModal)
    expect(syncConfirmationModal).toHaveLength(1)
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
      })
    })
  })
})
