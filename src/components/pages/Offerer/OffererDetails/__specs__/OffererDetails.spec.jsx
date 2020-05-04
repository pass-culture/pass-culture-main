import React from 'react'
import { shallow } from 'enzyme'
import OffererDetails from '../OffererDetails'
import { Offerer } from '../Offerer'
import BankInformation from '../BankInformation/BankInformation'

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

  describe('render', () => {
    it('should render a bank instructions block', () => {
      // given
      props.offerer.bic = null
      props.offerer.iban = null

      // when
      const wrapper = shallow(<OffererDetails {...props} />)

      // then
      const bankInstructions = wrapper.find(BankInformation)
      expect(bankInstructions).toHaveLength(1)
    })

    it('should render Venues', () => {
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
