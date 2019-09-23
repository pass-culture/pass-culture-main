import Offerer from '../Offerer'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | pages | Offerer', () => {
  let props

  beforeEach(() => {
    props = {
      adminUserOfferer: false,
      getOfferer: jest.fn(),
      getUserOfferers: jest.fn(),
      history: {
        push: jest.fn(),
      },
      match: {
        params: {
          offererId: 'AA',
        },
      },
      offerer: {
        bic: 'ABC',
        iban: 'DEF',
      },
      offererName: 'fake offerer name',
      query: {
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
      showNotification: jest.fn(),
      trackCreateOffererSuccess: jest.fn(),
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Offerer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('event tracking', () => {
    it('should track offerer creation', () => {
      // given
      const state = {}
      const action = {
        payload: {
          id: 'Ty5645dgfd',
        },
      }
      const wrapper = shallow(<Offerer {...props} />)

      // when
      wrapper.instance().onHandleSuccess(state, action)

      // then
      expect(props.trackCreateOffererSuccess).toHaveBeenCalledWith('Ty5645dgfd')
    })
  })

  describe('render', () => {
    it('should render a bank instructions block when bank information are not provided', () => {
      // given
      props.offerer.bic = null
      props.offerer.iban = null

      // when
      const wrapper = shallow(<Offerer {...props} />)

      // then
      const bankInstructions = wrapper.find('.bank-instructions-label')
      expect(bankInstructions).toHaveLength(1)
      expect(bankInstructions.text()).toBe(
        'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
      )
    })

    it('should not render a bank instructions block when bank information are provided', () => {
      // when
      const wrapper = shallow(<Offerer {...props} />)

      // then
      const bankInstructions = wrapper.find('.bank-instructions-label')
      expect(bankInstructions).toHaveLength(0)
    })

    it('should not render a bank instructions block when offerer name is not provided', () => {
      // given
      props.offererName = ''

      // when
      const wrapper = shallow(<Offerer {...props} />)

      // then
      const bankInstructions = wrapper.find('.bank-instructions-label')
      expect(bankInstructions).toHaveLength(0)
    })
  })
})
