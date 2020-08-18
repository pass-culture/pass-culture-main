import { shallow } from 'enzyme'
import React from 'react'
import Desk from '../Desk'

import DeskState from '../DeskState/DeskState'

describe('src | components | pages | Desk | Desk ', () => {
  const options = {
    disableLifecycleMethods: true,
  }
  let getBookingFromCode
  let validateBooking
  let props
  let trackValidateBookingSuccess

  beforeEach(() => {
    getBookingFromCode = jest.fn()
    trackValidateBookingSuccess = jest.fn()
    validateBooking = jest.fn()

    props = {
      getBookingFromCode,
      trackValidateBookingSuccess,
      validateBooking,
    }
  })

  it('should render Desk component with default state', () => {
    // when
    const wrapper = shallow(<Desk {...props} />, options)

    // then
    expect(wrapper.state('booking')).toBeNull()
    expect(wrapper.state('code')).toBe('')
    expect(wrapper.state('status')).toBe('CODE_ENTER')
  })

  describe('render', () => {
    describe('desk status', () => {
      it('should render DeskState component with proper props when status is enter a code', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Saisissez un code')
        expect(deskState.prop('booking')).toBeNull()
        expect(deskState.prop('level')).toBe('pending')
      })

      it('should render DeskState component with proper props when status is typing a code', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_TYPING' })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Caractères restants: 6/6')
        expect(deskState.prop('booking')).toBeNull()
        expect(deskState.prop('level')).toBe('pending')
      })

      it('should render DeskState component with proper props when status is invalid', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_SYNTAX_INVALID' })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Caractères valides : de A à Z et de 0 à 9')
        expect(deskState.prop('booking')).toBeNull()
        expect(deskState.prop('level')).toBe('error')
      })

      it('should render DeskState component with proper props when status is verification', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_VERIFICATION_IN_PROGRESS' })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Vérification...')
        expect(deskState.prop('booking')).toBeNull()
        expect(deskState.prop('level')).toBe('pending')
      })

      it('should render DeskState component with proper props when status is code already used', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_ALREADY_USED', booking: {} })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Ce coupon est déjà enregistré')
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('error')
      })

      it('should render DeskState component with proper props when status is code ok', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_VERIFICATION_SUCCESS', booking: {} })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe(
          'Coupon vérifié, cliquez sur "Valider" pour enregistrer'
        )
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('pending')
      })

      it('should render DeskState component with proper props when status is code registering', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({
          status: 'CODE_REGISTERING_IN_PROGRESS',
          booking: {},
        })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Enregistrement en cours...')
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('pending')
      })

      it('should render DeskState component with proper props when status is code registered', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_REGISTERING_SUCCESS', booking: {} })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('Enregistrement réussi !')
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('success')
      })

      it('should render DeskState component with proper props when status is code verification failed', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({
          status: 'CODE_VERIFICATION_FAILED',
          booking: {},
          message: 'fake message',
        })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('fake message')
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('error')
      })

      it('should render DeskState component with proper props when status is code registering failed', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({
          status: 'CODE_REGISTERING_FAILED',
          booking: {},
          message: 'fake message',
        })

        // then
        const deskState = wrapper.find(DeskState)
        expect(deskState).toHaveLength(1)
        expect(deskState.prop('message')).toBe('fake message')
        expect(deskState.prop('booking')).toStrictEqual({})
        expect(deskState.prop('level')).toBe('error')
      })
    })

    describe('validate button', () => {
      it('should render a button which is disabled by default when code is not ok', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)

        // then
        const button = wrapper.find('button')
        expect(button).toHaveLength(1)
        expect(button.prop('disabled')).toBe(true)
        expect(button.prop('className')).toBe('button')
        expect(button.prop('type')).toBe('submit')
        expect(button.prop('onClick')).toStrictEqual(expect.any(Function))
      })

      it('should render a button which is enabled when code is ok', () => {
        // when
        const wrapper = shallow(<Desk {...props} />, options)
        wrapper.setState({ status: 'CODE_VERIFICATION_SUCCESS' })

        // then
        const button = wrapper.find('button')
        expect(button).toHaveLength(1)
        expect(button.prop('disabled')).toBe(false)
      })
    })
  })

  describe('functions', () => {
    describe('handleSuccessWhenGetBookingFromCode', () => {
      it('should update state status to code already used when a booking is retrieved and is validated', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const booking = {
          isValidated: true,
        }
        const state = {}
        const action = {
          payload: {
            datum: booking,
          },
        }

        // when
        wrapper.instance().handleSuccessWhenGetBookingFromCode(state, action)

        // then
        expect(wrapper.state('status')).toBe('CODE_ALREADY_USED')
        expect(wrapper.state('booking')).toBe(booking)
      })

      it('should update state status to code ok when a booking is not validated', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const booking = {
          isValidated: false,
        }
        const state = {}
        const action = {
          payload: {
            datum: booking,
          },
        }

        // when
        wrapper.instance().handleSuccessWhenGetBookingFromCode(state, action)

        // then
        expect(wrapper.state('status')).toBe('CODE_VERIFICATION_SUCCESS')
        expect(wrapper.state('booking')).toBe(booking)
      })
    })

    describe('handleFailWhenGetBookingFromCode', () => {
      it('should update state with code verification failed status and error message when booking retrieval failed', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const state = {}
        const action = {
          payload: {
            errors: [{ 1: 'error1' }, { 2: 'error2' }],
          },
        }

        // when
        wrapper.instance().handleFailWhenGetBookingFromCode(state, action)

        // then
        expect(wrapper.state('status')).toBe('CODE_VERIFICATION_FAILED')
        expect(wrapper.state('message')).toBe('error1 error2')
      })
    })

    describe('validateBooking', () => {
      it('should dispatch an action to validate booking using code', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)

        // when
        wrapper.instance().handleCodeRegistration('ABCDEF')
        //wrapper.instance().handleSuccessWhenValidateBookin = jest.fn()

        // then
        expect(props.validateBooking).toHaveBeenCalledWith(
          'ABCDEF',
          undefined,
          expect.any(Function)
        )
      })
    })

    describe('handleSuccessWhenValidateBooking', () => {
      it('should update state status to code registered when code is registered successfully', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)

        // when
        wrapper.instance().handleSuccessWhenValidateBooking()

        // then
        expect(wrapper.state('status')).toBe('CODE_REGISTERING_SUCCESS')
      })
    })

    describe('handleFailWhenValidateBooking', () => {
      it('should update state with code registering failed status and error message when code is not validated successfully', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const state = {}
        const action = {
          payload: {
            errors: [{ 1: 'error1' }, { 2: 'error2' }],
          },
        }

        // when
        wrapper.instance().handleFailWhenValidateBooking(state, action)

        // then
        expect(wrapper.state('status')).toBe('CODE_REGISTERING_FAILED')
        expect(wrapper.state('message')).toBe('error1 error2')
      })
    })

    describe('handleCodeChange', () => {
      it('should update status to code enter when code from input is empty', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const event = {
          target: {
            value: '',
          },
        }

        // when
        wrapper.instance().handleCodeChange(event)

        // then
        expect(wrapper.state('status')).toBe('CODE_ENTER')
      })

      it('should update status to code invalid when code from input is composed of invalid characters', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const event = {
          target: {
            value: 'ù^^``',
          },
        }

        // when
        wrapper.instance().handleCodeChange(event)

        // then
        expect(wrapper.state('status')).toBe('CODE_SYNTAX_INVALID')
      })

      it('should update status to code typing when code from input is lesser than 6 characters', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const event = {
          target: {
            value: 'ABCDE',
          },
        }

        // when
        wrapper.instance().handleCodeChange(event)

        // then
        expect(wrapper.state('status')).toBe('CODE_TYPING')
      })

      it('should update status to code verification when code respects format and number of characters', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const event = {
          target: {
            value: 'ABCDEF',
          },
        }

        // when
        wrapper.instance().handleCodeChange(event)

        // then
        expect(wrapper.state('status')).toBe('CODE_VERIFICATION_IN_PROGRESS')
      })

      it('should retrieve a booking information using code from input', () => {
        // given
        const wrapper = shallow(<Desk {...props} />, options)
        const event = {
          target: {
            value: 'ABCDEF',
          },
        }
        const input = wrapper.find('input')

        // when
        input.simulate('change', event)

        // then
        expect(wrapper.state('status')).toBe('CODE_VERIFICATION_IN_PROGRESS')
        expect(props.getBookingFromCode).toHaveBeenCalledWith(
          'ABCDEF',
          expect.any(Function),
          expect.any(Function)
        )
      })
    })
  })
})
