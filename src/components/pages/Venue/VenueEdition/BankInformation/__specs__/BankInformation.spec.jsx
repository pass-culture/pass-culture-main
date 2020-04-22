import React from 'react'
import { shallow } from 'enzyme'
import BankInformation from '../BankInformation'

jest.mock('../../../../../../utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

describe('src | Venue | BankInformation ', () => {
  const venue = {
    id: 'AA',
    name: 'fake venue name',
  }
  const offerer = {}

  let props
  beforeEach(() => {
    props = { venue, offerer }
  })
  it('should render instruction block when banking information are not provided', () => {
    // Given
    props.venue = {
      id: 'AA',
      name: 'fake venue name',
      bic: null,
      iban: null,
    }
    props.offerer = {
      id: 'BB',
      name: 'fake offerer name',
    }

    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const bankInstructions = wrapper.find({
      children:
        'Renseigner vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles',
    })
    const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
    expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
      'link/to/venue/demarchesSimplifiees/procedure'
    )
    expect(bankInstructions).toHaveLength(1)
  })

  it('should render offerer information when venue banking information are not provided', () => {
    // Given
    props.venue = {
      id: 'AA',
      name: 'fake venue name',
      bic: null,
      iban: null,
    }
    props.offerer = {
      id: 'BB',
      name: 'fake offerer name',
      bic: 'offererBic',
      iban: 'offererIban',
    }

    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const expectedBic = wrapper.find({ children: 'offererBic' })
    const expectedIban = wrapper.find({ children: 'offererIban' })
    expect(expectedBic).toHaveLength(1)
    expect(expectedIban).toHaveLength(1)
  })

  it('should render venue information when venue and offerer banking information are both provided', () => {
    // Given
    props.venue = {
      id: 'AA',
      name: 'fake venue name',
      bic: 'venueBic',
      iban: 'venueIban',
    }
    props.offerer = {
      id: 'BB',
      name: 'fake offerer name',
      bic: 'offererBic',
      iban: 'offererIban',
    }

    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const expectedBic = wrapper.find({ children: 'venueBic' })
    const expectedIban = wrapper.find({ children: 'venueIban' })
    expect(expectedBic).toHaveLength(1)
    expect(expectedIban).toHaveLength(1)
  })

  it('should render modification block when BIC and IBAN are provided', () => {
    // when
    props.venue = {
      bic: 'ABC',
      iban: 'DEF',
    }
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const bankInstructions = wrapper.find({
      children:
        'Les remboursements des offres éligibles présentées dans ce lieu sont effectués sur le compte ci-dessous :',
    })
    expect(bankInstructions).toHaveLength(1)
    const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
    expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
      'link/to/venue/demarchesSimplifiees/procedure'
    )
  })
})
