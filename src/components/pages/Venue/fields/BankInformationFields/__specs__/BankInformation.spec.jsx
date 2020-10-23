import React from 'react'
import { shallow } from 'enzyme'
import BankInformation from '../BankInformationFields'
import { BicIbanFields } from '../BicIbanFields'
import { ApplicationBanner } from '../ApplicationBanner'

jest.mock('utils/config', () => ({
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

  describe('when no application has been made or application has been refused', () => {
    describe('when the offerer has no bank information', () => {
      it('should render instruction block', () => {
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
            'Renseignez vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles',
        })
        const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
        expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
          'link/to/venue/demarchesSimplifiees/procedure'
        )
        expect(bankInstructions).toHaveLength(1)
      })
    })

    describe('when the offerer has bank information', () => {
      it('should render offerer information', () => {
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
        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(true)
        expect(bicIbanFields.prop('iban')).toBe('offererIban')
        expect(bicIbanFields.prop('bic')).toBe('offererBic')
      })
    })
  })

  describe('when application has been validated', () => {
    describe('when venue and offerer banking information are both provided', () => {
      it('should render venue informations', () => {
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
        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(true)
        expect(bicIbanFields.prop('iban')).toBe('venueIban')
        expect(bicIbanFields.prop('bic')).toBe('venueBic')
      })
    })
  })

  describe('when application is in construction or in instruction', () => {
    describe('when offerer has no bank informations', () => {
      it('should render current application detail', () => {
        // Given
        props.venue = {
          id: 'AA',
          name: 'fake venue name',
          bic: null,
          iban: null,
          demarchesSimplifieesApplicationId: '12',
        }

        // when
        const wrapper = shallow(<BankInformation {...props} />)

        // then
        const applicationBanner = wrapper.find(ApplicationBanner)
        expect(applicationBanner.exists()).toBe(true)
        expect(applicationBanner.prop('applicationId')).toBe('12')
      })
    })

    describe('when offerer has bank informations', () => {
      it('should render current application detail and offerer bank informations', () => {
        // Given
        props.venue = {
          id: 'AA',
          name: 'fake venue name',
          bic: null,
          iban: null,
          demarchesSimplifieesApplicationId: '12',
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
        const applicationBanner = wrapper.find(ApplicationBanner)
        expect(applicationBanner.exists()).toBe(true)
        expect(applicationBanner.prop('applicationId')).toBe('12')

        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(true)
        expect(bicIbanFields.prop('iban')).toBe('offererIban')
        expect(bicIbanFields.prop('bic')).toBe('offererBic')
      })

      it('should render modification block when BIC and IBAN are provided', () => {
        // Given
        props.venue = {
          bic: 'ABC',
          iban: 'DEF',
        }

        // when
        const wrapper = shallow(<BankInformation {...props} />)

        // then
        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(true)
        expect(bicIbanFields.prop('iban')).toBe('DEF')
        expect(bicIbanFields.prop('bic')).toBe('ABC')
      })

      it('should render current application detail when demarchesSimplifieesApplicationId is provided', () => {
        // Given
        props.venue = {
          id: 'AA',
          name: 'fake venue name',
          bic: null,
          iban: null,
          demarchesSimplifieesApplicationId: '12',
        }

        // when
        const wrapper = shallow(<BankInformation {...props} />)

        // then
        const applicationBanner = wrapper.find(ApplicationBanner)
        expect(applicationBanner.exists()).toBe(true)
        expect(applicationBanner.prop('applicationId')).toBe('12')

        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(false)
      })

      it('should render current application detail and offerer bank informations when both presents in props', () => {
        // Given
        props.venue = {
          id: 'AA',
          name: 'fake venue name',
          bic: null,
          iban: null,
          demarchesSimplifieesApplicationId: '12',
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
        const applicationBanner = wrapper.find(ApplicationBanner)
        expect(applicationBanner.exists()).toBe(true)
        expect(applicationBanner.prop('applicationId')).toBe('12')

        const bicIbanFields = wrapper.find(BicIbanFields)
        expect(bicIbanFields.exists()).toBe(true)
        expect(bicIbanFields.prop('iban')).toBe('offererIban')
        expect(bicIbanFields.prop('bic')).toBe('offererBic')
      })
    })
  })
})
