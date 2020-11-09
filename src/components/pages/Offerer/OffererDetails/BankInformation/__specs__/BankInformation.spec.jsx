import { shallow } from 'enzyme'
import React from 'react'

import { Offerer } from '../../Offerer'
import BankInformation from '../BankInformation'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/offerer/demarchesSimplifiees/procedure',
}))

const reimbursementBannerPresent = wrapper => {
  expect(wrapper.find('Banner').last().props()).toStrictEqual({
    type: 'notification-info',
    linkTitle: 'En savoir plus sur les remboursements',
    href:
      'https://aide.passculture.app/fr/article/acteurs-determiner-ses-modalites-de-remboursement-1ab6g2m/',
    icon: 'ico-external-site',
    subtitle: '',
  })
}

describe('src | Offerer | BankInformation', () => {
  it('should render instruction block when banking information are not provided', () => {
    // Given
    const offererWithoutBankInformation = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: null,
      iban: null,
    })

    // when
    const wrapper = shallow(<BankInformation offerer={offererWithoutBankInformation} />)

    // then
    expect(wrapper.find('Banner').first().props()).toStrictEqual({
      type: 'attention',
      subtitle: 'Renseignez vos coordonnées bancaires pour être remboursé de vos offres éligibles',
      linkTitle: 'Renseignez les coordonnées bancaires de la structure',
      href: 'link/to/offerer/demarchesSimplifiees/procedure',
      icon: 'ico-external-site',
    })
    reimbursementBannerPresent(wrapper)
  })

  it('should render instruction block when BIC and IBAN are provided', () => {
    // given
    const offererWithBankInformation = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: 'offererBic',
      iban: 'offererIban',
      demarchesSimplifieesApplicationId: '12',
    })

    // when
    const wrapper = shallow(<BankInformation offerer={offererWithBankInformation} />)

    // then
    const bankInstructions = wrapper.find({
      children:
        'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres :',
    })
    expect(bankInstructions).toHaveLength(1)
    const expectedBic = wrapper.find({ children: 'offererBic' })
    const expectedIban = wrapper.find({ children: 'offererIban' })
    expect(expectedBic).toHaveLength(1)
    expect(expectedIban).toHaveLength(1)
    const linkToDemarcheSimplifieeProcedure = wrapper.find('a')
    expect(linkToDemarcheSimplifieeProcedure.prop('href')).toBe(
      'link/to/offerer/demarchesSimplifiees/procedure'
    )
    reimbursementBannerPresent(wrapper)
  })

  it('should render current application detail when demarchesSimplifieesApplicationId is provided', () => {
    // Given
    const offererWithoutBankInformation = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: null,
      iban: null,
      demarchesSimplifieesApplicationId: '12',
    })

    // when
    const wrapper = shallow(<BankInformation offerer={offererWithoutBankInformation} />)

    // then
    expect(wrapper.find('Banner').first().props()).toStrictEqual({
      type: 'attention',
      subtitle: 'Votre dossier est en cours pour cette structure',
      linkTitle: 'Accéder au dossier',
      href: 'https://www.demarches-simplifiees.fr/dossiers/12',
      icon: 'ico-external-site',
    })
    reimbursementBannerPresent(wrapper)
  })
})
