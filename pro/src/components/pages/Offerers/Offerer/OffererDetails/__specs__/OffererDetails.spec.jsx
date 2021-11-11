/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt rtl "Gaël: migration from enzyme to RTL"
*/

import { shallow } from 'enzyme'
import React from 'react'

import BankInformation from '../BankInformation/BankInformation'
import { Offerer } from '../Offerer'
import OffererDetails from '../OffererDetails'
import VenuesContainer from '../Venues/VenuesContainer'

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
    it('should render a bank instructions block if they are already provided', () => {
      // given
      props.offerer.bic = 'FR7630001001111111111111111'
      props.offerer.iban = 'QS111111111'

      // when
      const wrapper = shallow(<OffererDetails {...props} />)

      // then
      const bankInstructions = wrapper.find(BankInformation)
      expect(bankInstructions).toHaveLength(1)
    })

    it('should render Venues', () => {
      // when
      const wrapper = shallow(<OffererDetails {...props} />)
      const venuesComponent = wrapper.find(VenuesContainer)

      // then
      expect(venuesComponent).toHaveLength(1)
      expect(venuesComponent.prop('offererId')).toBe(props.offerer.id)
      expect(venuesComponent.prop('venues')).toBe(props.venues)
    })
  })
})
