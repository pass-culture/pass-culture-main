import { shallow } from 'enzyme'
import React from 'react'

import { BicIbanFields } from '../BicIbanFields'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

describe('src | Venue | BicIbanFields', () => {
  it('should display bank informations', () => {
    const props = {
      bic: '123 456 789',
      iban: 'FRBICAVECUNEVALEURPARDEFAUT',
    }

    //
    const wrapper = shallow(<BicIbanFields {...props} />)

    // then
    expect(wrapper).toHaveLength(1)
    const bic = wrapper.find({ children: '123 456 789' })
    const iban = wrapper.find({ children: 'FRBICAVECUNEVALEURPARDEFAUT' })
    expect(bic.exists()).toBe(true)
    expect(iban.exists()).toBe(true)
  })

  it('should display modification link', () => {
    const props = {
      bic: '123 456 789',
      iban: 'FRBICAVECUNEVALEURPARDEFAUT',
    }

    //
    const wrapper = shallow(<BicIbanFields {...props} />)

    // then
    const modificationLink = wrapper.find('a')
    expect(modificationLink.exists()).toBe(true)
    expect(modificationLink.prop('href')).toBe('link/to/venue/demarchesSimplifiees/procedure')
  })
})
