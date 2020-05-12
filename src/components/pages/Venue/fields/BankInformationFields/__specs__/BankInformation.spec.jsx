import React from 'react'
import { shallow } from 'enzyme'
import BankInformation from '../BankInformationFields'

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
        const expectedBic = wrapper.find({ children: 'offererBic' })
        const expectedIban = wrapper.find({ children: 'offererIban' })
        expect(expectedBic).toHaveLength(1)
        expect(expectedIban).toHaveLength(1)
      })
    })
  })

  describe('when application has been validated', () => {
    describe('when venue and offerer banking information are both provided', () => {
      it('should render venue information', () => {
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
        const modificationLink = wrapper.findWhere(node => node.text() === 'Modifier').first()
        const expectedBic = wrapper.find({ children: 'venueBic' })
        const expectedIban = wrapper.find({ children: 'venueIban' })
        expect(expectedBic).toHaveLength(1)
        expect(expectedIban).toHaveLength(1)
        expect(modificationLink).toHaveLength(1)
      })
    })

    describe('when venue banking information are provided', () => {
      it('should render modification block', () => {
        // Given
        props.venue = {
          bic: 'ABC',
          iban: 'DEF',
        }

        // when
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
          demarchesSimplifieesApplicationId: 12,
        }

        // when
        const wrapper = shallow(<BankInformation {...props} />)

        // then
        const bankInstructions = wrapper.find({
          children: 'Votre dossier est en cours pour ce lieu',
        })
        const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
        expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
          'https://www.demarches-simplifiees.fr/dossiers/12'
        )
        expect(bankInstructions).toHaveLength(1)
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
          demarchesSimplifieesApplicationId: 12,
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
        const bankInstructions = wrapper.find({
          children: 'Votre dossier est en cours pour ce lieu',
        })

        const modificationLink = wrapper.findWhere(node => node.text() === 'Modifier').first()
        const linkToDemarcheSimplifieeProcedure = wrapper
          .findWhere(
            node => node.prop('href') === 'https://www.demarches-simplifiees.fr/dossiers/12'
          )
          .first()

        expect(linkToDemarcheSimplifieeProcedure).toHaveLength(1)
        expect(modificationLink).toHaveLength(0)
        expect(bankInstructions).toHaveLength(1)
        const expectedBic = wrapper.find({ children: 'offererBic' })
        const expectedIban = wrapper.find({ children: 'offererIban' })
        expect(expectedBic).toHaveLength(1)
        expect(expectedIban).toHaveLength(1)
      })
    })
  })
})
