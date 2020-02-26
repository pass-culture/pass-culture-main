import React from 'react'
import { mount, shallow } from 'enzyme'

import { Form } from 'react-final-form'
import NumberField from '../../../../../layout/form/fields/NumberField'
import Icon from '../../../../../layout/Icon'

import AllocineProviderForm from '../../AllocineProviderForm/AllocineProviderForm'
import SynchronisationConfirmationModal from '../SynchronisationConfirmationModal/SynchronisationConfirmationModal'

describe('components | AllocineProviderForm', () => {
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
    const offerImportButton = wrapper.find({
      children: `Importer les offres`,
    })
    expect(offerImportButton).toHaveLength(1)
    expect(offerImportButton.type()).toBe('button')
  })

  it('should display the price field with minimum value set to 0', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceFieldLabel =  wrapper
      .findWhere(node => node.text() === 'Prix de vente/place ')
      .first()

    const priceFieldInput =  wrapper
      .findWhere(node => node.prop('placeholder') === 'Ex : 12€')
      .first()

    expect(priceFieldLabel).toHaveLength(1)
    expect(priceFieldInput).toHaveLength(1)
    expect(priceFieldInput.prop('min')).toBe('0')
    expect(priceFieldInput.prop('required')).toBe(true)
  })

  it('should display the available field with default value set to Illimité', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const availableInputLabel = wrapper.find({
      children: `Nombre de places/séance`,
    })

    const availableInput =  wrapper
      .findWhere(node => node.prop('placeholder') === 'Illimité')
      .first()

    expect(availableInputLabel).toHaveLength(1)
    expect(availableInput).toHaveLength(1)
  })

  it('should display the isDuo checkbox with default value checked=false', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const isDuoCheckboxLabel = wrapper.find({
      children: `Accepter les réservations DUO`,
    })

    const isDuoCheckbox = wrapper.findWhere(node => node.prop('type') === 'checkbox').first()

    expect(isDuoCheckboxLabel).toHaveLength(1)
    expect(isDuoCheckbox).toHaveLength(1)
  })

  it('should display a tooltip and an Icon component for price field', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceToolTip =  wrapper
      .findWhere(node => node.prop('data-tip') === '<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>')
      .first()

    const toolTipIcon = priceToolTip.find(Icon)


    expect(priceToolTip).toHaveLength(1)
    expect(toolTipIcon).toHaveLength(1)
    expect(toolTipIcon.prop('svg')).toBe('picto-info')
  })


  it('should display a tooltip and an Icon component for isDuo field', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceSection = wrapper.find(Form).find('.apf-isDuo-section')
    const tooltip = priceSection.find('.apf-tooltip')
    expect(tooltip).toHaveLength(1)
    expect(tooltip.prop('data-place')).toBe('bottom')
    expect(tooltip.prop('data-tip')).toBe(
      '<p>En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur.</p>'
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
        available: 50
      }
      const wrapper = shallow(<AllocineProviderForm {...props} />)

      // when
      wrapper.instance().handleSubmit(formValues, {})

      // then
      expect(wrapper.state('isLoadingMode')).toBe(true)
      expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
        price: 12,
        available: 50,
        providerId: 'AA',
        venueId: 'BB',
      })
    })
  })
})
