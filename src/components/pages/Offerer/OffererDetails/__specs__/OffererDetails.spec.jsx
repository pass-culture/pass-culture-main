import React from 'react'
import { shallow } from 'enzyme'
import OffererDetails from '../OffererDetails'
import { Offerer } from '../Offerer'

describe('src | components | pages | Offerer | OffererDetails', () => {
  let props
  beforeEach(() => {
    props = {
      loadOffererById: () => {},
      offerer: new Offerer({
        id: 'AA',
        name: 'fake offerer name',
        address: 'fake address',
        bic: 'ABC',
        iban: 'DEF',
      }),
      offererId: 'AA',
      venues: [{}],
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<OffererDetails {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('bank information', () => {
      it('should render a bank instructions block when bank information are not provided', () => {
        // given
        props.offerer.bic = null
        props.offerer.iban = null

        // when
        const wrapper = shallow(<OffererDetails {...props} />)

        // then
        const bankInstructions = wrapper.find('.bank-instructions-label')
        expect(bankInstructions).toHaveLength(1)
        expect(bankInstructions.text()).toBe(
          'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
        )
      })

      it('should not render a bank instructions block when bank information are provided', () => {
        // when
        const wrapper = shallow(<OffererDetails {...props} />)

        // then
        const bankInstructions = wrapper.find('.bank-instructions-label')
        expect(bankInstructions).toHaveLength(0)
      })
    })

    describe('venues information', () => {
      it('should render a Venues Tooltip', () => {
        // when
        const wrapper = shallow(<OffererDetails {...props} />)
        const venuesComponent = wrapper.find('Venues')

        // then
        expect(venuesComponent).toHaveLength(1)
        expect(venuesComponent.prop('offererId')).toBe(props.offerer.id)
        expect(venuesComponent.prop('venues')).toBe(props.venues)
      })
    })
  })
})
