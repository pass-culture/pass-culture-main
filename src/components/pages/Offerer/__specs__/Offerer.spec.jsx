import Offerer from '../Offerer'
import React from 'react'
import { shallow } from 'enzyme'
import { OffererClass } from '../OffererClass'

describe('src | components | pages | Offerer', () => {
  let props
  const offerer = {
    id: 'AA',
    name: 'fake offerer name',
    address: 'fake address',
    bic: 'ABC',
    iban: 'DEF',
  }
  const adminUserOfferer = {}
  beforeEach(() => {
    props = {
      offerer: new OffererClass(offerer, adminUserOfferer),
      getOfferer: jest.fn(),
      getUserOfferers: jest.fn(),
      history: {
        push: jest.fn(),
      },
      query: {
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
      showNotification: jest.fn(),
      trackCreateOfferer: jest.fn(),
      trackModifyOfferer: jest.fn(),
      venues: [],
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
          datum: {
            id: 'Ty5645dgfd',
          },
        },
      }
      const wrapper = shallow(<Offerer {...props} />)

      // when
      wrapper.instance().onHandleSuccess(state, action)

      // then
      expect(props.trackCreateOfferer).toHaveBeenCalledWith('Ty5645dgfd')
    })

    it('should track offerer modification', () => {
      // given
      const state = {}
      const action = {
        payload: {
          datum: {
            id: 'Ty5645dgfd',
          },
        },
      }
      jest.spyOn(props.query, 'context').mockReturnValue({
        isCreatedEntity: false,
      })
      const wrapper = shallow(<Offerer {...props} />)

      // when
      wrapper.instance().onHandleSuccess(state, action)

      // then
      expect(props.trackModifyOfferer).toHaveBeenCalledWith('AA')
    })
  })

  describe('render', () => {
    describe('bank informations', () => {
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
        props.offerer.name = ''

        // when
        const wrapper = shallow(<Offerer {...props} />)

        // then
        const bankInstructions = wrapper.find('.bank-instructions-label')
        expect(bankInstructions).toHaveLength(0)
      })
    })

    describe('venues information', () => {
      it('should render a Venues Component', () => {
        // given
        props.venues = [{}, {}, {}]

        jest.spyOn(props.query, 'context').mockReturnValue({
          isCreatedEntity: false,
        })

        // when
        const wrapper = shallow(<Offerer {...props} />)
        const venuesComponent = wrapper.find('Venues')

        // then
        expect(venuesComponent).toHaveLength(1)
      })
    })
  })
})
