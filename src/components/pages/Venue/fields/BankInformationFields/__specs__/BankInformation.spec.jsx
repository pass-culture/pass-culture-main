import { shallow } from 'enzyme'
import React from 'react'

import { ApplicationBanner } from '../ApplicationBanner'
import BankInformation from '../BankInformationFields'
import { BicIbanFields } from '../BicIbanFields'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

describe('src | Venue | BankInformation', () => {
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
        expect(wrapper.find('Banner').first().props()).toStrictEqual({
          type: 'attention',
          subtitle:
            'Renseignez vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles',
          linkTitle: 'Renseignez les coordonnées bancaires du lieu',
          href: 'link/to/venue/demarchesSimplifiees/procedure',
          icon: 'ico-external-site',
        })
        expect(wrapper.find('Banner').last().props()).toStrictEqual({
          type: 'notification-info',
          linkTitle: 'En savoir plus sur les remboursements',
          href:
            'https://aide.passculture.app/fr/article/acteurs-determiner-ses-modalites-de-remboursement-1ab6g2m/',
          icon: 'ico-external-site',
          subtitle: '',
        })
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
