import { shallow, mount } from 'enzyme'
import moment from 'moment'
import React from 'react'
import { Field } from 'react-final-form'

import CheckBoxField from '../../../../../forms/inputs/CheckBoxField'
import SelectField from '../../../../../forms/inputs/SelectField'
import BookingFormContent from '../BookingFormContent'

describe('bookingFormContent', () => {
  let props
  let handleSubmit

  beforeEach(() => {
    handleSubmit = jest.fn()
    props = {
      extraClassName: 'fake className',
      formId: 'fake formId',
      invalid: false,
      isStockDuo: false,
      isEvent: false,
      isReadOnly: false,
      handleSubmit,
      onChange: jest.fn(),
      offerId: 'o1',
      values: {
        bookables: [],
        date: null,
        price: null,
      },
    }
  })

  it('should render a form element with the proper props when is not read only mode', () => {
    // when
    const wrapper = mount(<BookingFormContent {...props} />)

    // then
    const form = wrapper.find('form')
    expect(form).toHaveLength(1)
    expect(form.prop('className')).toBe('fake className ')
    expect(form.prop('id')).toBe('fake formId')
    expect(form.prop('onSubmit')).toStrictEqual(handleSubmit)
  })

  it('should render a form element with the proper props when is read only mode', () => {
    // given
    props.isReadOnly = true

    // when
    const wrapper = mount(<BookingFormContent {...props} />)

    // then
    const form = wrapper.find('form')
    expect(form).toHaveLength(1)
    expect(form.prop('className')).toBe('fake className is-read-only')
    expect(form.prop('id')).toBe('fake formId')
    expect(form.prop('onSubmit')).toStrictEqual(handleSubmit)
  })

  describe('when booking a Duo offer', () => {
    it('should display a field and checkbox', () => {
      // given
      props.isStockDuo = true
      props.isEvent = true
      props.values = {
        bookables: [
          {
            id: 'B1',
          },
        ],
        date: '21/10/2001',
        price: 5,
      }

      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      const field = wrapper.find(Field)
      const checkBoxField = wrapper.find(CheckBoxField)
      expect(field).toHaveLength(1)
      expect(checkBoxField).toHaveLength(1)
    })
  })

  describe('when booking an event', () => {
    beforeEach(() => {
      props.isEvent = true
    })

    it('should display a notice regarding the withdrawal period', () => {
      // given
      props.isEvent = true
      props.values = {
        bookables: [
          {
            id: 'B1',
          },
        ],
        date: '21/10/2001',
        price: 5,
      }

      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      expect(wrapper.find(
        { children: 'Réservation annulable dans les 48h suivants la réservation et moins de 72h avant la date de l’évènement (si applicable)' }
      )).toHaveLength(1)
    })

    it('should render a Field component with the proper props', () => {
      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      const field = wrapper.find(Field)
      expect(field).toHaveLength(1)
      expect(field.prop('name')).toBe('date')
      expect(field.prop('render')).toStrictEqual(expect.any(Function))
    })

    it('should not render a SelectField component when no date has been selected', () => {
      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      const selectField = wrapper.find(SelectField)
      expect(selectField).toHaveLength(0)
    })

    it('should display the selected date if one has been selected', () => {
      // given
      const date = moment().add(3, 'days')
      props.values = {
        bookables: [
          {
            beginningDatetime: date,
            id: 'AE',
            price: 12,
          },
          {
            beginningDatetime: date,
            id: 'AF',
            price: 13,
          },
        ],
        date,
      }

      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      const selectField = wrapper.find(SelectField)
      expect(selectField).toHaveLength(1)
      expect(selectField.props()).toStrictEqual({
        className: 'text-center',
        disabled: false,
        id: 'booking-form-time-picker-field',
        label: 'Choisis une heure :',
        name: 'time',
        placeholder: 'Heure et prix',
        options: [
          {
            id: 'AE',
            label: `${date.format('HH:mm')} - 12\u00A0€`,
          },
          {
            id: 'AF',
            label: `${date.format('HH:mm')} - 13\u00A0€`,
          },
        ],
        readOnly: false,
        required: false,
      })
    })
  })

  describe('when booking a thing', () => {
    beforeEach(() => {
      props.isEvent = false
    })
    it('should display the corresponding messages', () => {
      // given
      props.values = {
        bookables: [],
        date: '2019-01-01',
        price: 12,
      }

      // when
      const wrapper = shallow(<BookingFormContent {...props} />)

      // then
      expect(wrapper.find({ children: 'Tu es sur le point de réserver' })).toHaveLength(1)
      expect(wrapper.find({ children: 'cette offre pour 12 €.' })).toHaveLength(1)
    })
  })
})
