import React from 'react'
import { mount, shallow } from 'enzyme'

import { Form } from 'react-final-form'
import NumberField from '../../../../../../layout/form/fields/NumberField'
import Icon from '../../../../../../layout/Icon'
import AllocineProviderForm from '../../AllocineProviderForm/AllocineProviderForm'
import CheckboxField from '../../../../../../layout/form/fields/CheckboxField'

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
    })
  })

  it('should display the price field with minimum value set to 0', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const priceFieldLabel = wrapper
      .findWhere(node => node.text() === 'Prix de vente/place ')
      .first()

    const priceFieldInput = wrapper
      .findWhere(node => node.prop('placeholder') === 'Ex : 12€')
      .first()

    expect(priceFieldLabel).toHaveLength(1)
    expect(priceFieldInput).toHaveLength(1)
    expect(priceFieldInput.prop('min')).toBe('0')
  })

  it('should display the quantity field with default value set to Illimité', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const quantityInputLabel = wrapper.find({
      children: `Nombre de places/séance`,
    })

    const quantityInput = wrapper.findWhere(node => node.prop('placeholder') === 'Illimité').first()

    expect(quantityInputLabel).toHaveLength(1)
    expect(quantityInput).toHaveLength(1)
  })

  it('should display the isDuo checkbox unchecked by default', () => {
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
    const priceToolTip = wrapper
      .findWhere(
        node =>
          node.prop('data-tip') ===
          '<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue.</p>'
      )
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
    const isDuoToolTip = wrapper
      .findWhere(
        node =>
          node.prop('data-tip') ===
          '<p>En activant cette option, vous permettez au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur.</p>'
      )
      .first()

    const isDuoToolTipIcon = isDuoToolTip.find(Icon)

    expect(isDuoToolTip).toHaveLength(1)
    expect(isDuoToolTipIcon).toHaveLength(1)
    expect(isDuoToolTipIcon.prop('svg')).toBe('picto-info')
  })

  it('should display an import button disabled by default', () => {
    // when
    const wrapper = mount(<AllocineProviderForm {...props} />)

    // then
    const offerImportButton = wrapper.find({
      children: `Importer les offres`,
    })

    expect(offerImportButton).toHaveLength(1)
    expect(offerImportButton.prop('type')).toBe('submit')
    expect(offerImportButton.prop('disabled')).toBe(true)
  })

  it('should get checkbox value when form is submitted', () => {
    // given
    const props = {
      id: 'checkbox-id',
      name: 'checkbox-name',
      label: 'checkbox-label',
    }

    function formWithCheckboxField({ handleSubmit }) {
      return (
        <form>
          <CheckboxField {...props} />
          <button onClick={handleSubmit} type="submit">
            {'Submit'}
          </button>
        </form>
      )
    }

    const wrapper = mount(<Form onSubmit={handleOnSubmit} render={formWithCheckboxField} />)

    // when
    wrapper.find('input').simulate('change', { target: { value: true } })

    wrapper.find('button[type="submit"]').simulate('click')

    // then
    function handleOnSubmit(formValues) {
      expect(formValues['checkbox-name']).toBe(true)
    }
  })

  it('should be able to submit with filled payload when price field is filled', () => {
    // given
    const wrapper = mount(<AllocineProviderForm {...props} />)
    const formSubmit = wrapper.find('button')
    const priceSection = wrapper.findWhere(node => node.text() === 'Prix de vente/place *')
    const priceInput = priceSection.find(NumberField).find('input')
    priceInput.simulate('change', { target: { value: 10 } })

    // when
    formSubmit.simulate('click')

    // then
    expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
      price: 10,
      quantity: undefined,
      isDuo: true,
      providerId: 'AA',
      venueId: 'BB',
    })
  })

  it('should be able to submit with filled payload when price field is filled to 0', () => {
    // given
    const wrapper = mount(<AllocineProviderForm {...props} />)
    const formSubmit = wrapper.find('button')
    const priceSection = wrapper.findWhere(node => node.text() === 'Prix de vente/place *')
    const priceInput = priceSection.find(NumberField).find('input')
    priceInput.simulate('change', { target: { value: 0 } })

    // when
    formSubmit.simulate('click')

    // then
    expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
      price: 0,
      quantity: undefined,
      isDuo: true,
      providerId: 'AA',
      venueId: 'BB',
    })
  })

  it('should be able to submit with filled payload when price field is filled with a decimal', () => {
    // given
    const wrapper = mount(<AllocineProviderForm {...props} />)
    const submitButton = wrapper.find('button')
    const priceSection = wrapper.findWhere(node => node.text() === 'Prix de vente/place *')
    const priceInput = priceSection.find(NumberField).find('input')
    priceInput.simulate('change', { target: { value: '0,42' } })

    // when
    submitButton.simulate('click')

    // then
    expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
      price: 0.42,
      quantity: undefined,
      isDuo: true,
      providerId: 'AA',
      venueId: 'BB',
    })
  })

  it('should not be able to submit when quantity is filled but price is not', () => {
    // given
    const wrapper = mount(<AllocineProviderForm {...props} />)
    const form = wrapper.find('form')
    const quantitySection = wrapper.findWhere(node => node.text() === 'Nombre de places/séance')
    const quantityInput = quantitySection.find(NumberField).find('input')

    quantityInput.simulate('change', { target: { value: 10 } })

    // when
    form.simulate('click')

    // then
    expect(createVenueProvider).not.toHaveBeenCalled()
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
        quantity: 50,
        isDuo: true,
      }
      const wrapper = shallow(<AllocineProviderForm {...props} />)

      // when
      wrapper.instance().handleSubmit(formValues, {})

      // then
      expect(createVenueProvider).toHaveBeenCalledWith(expect.any(Function), expect.any(Function), {
        price: 12,
        quantity: 50,
        isDuo: true,
        providerId: 'AA',
        venueId: 'BB',
      })
    })
  })
})
