import { shallow } from 'enzyme'
import React from 'react'

import DisplayButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import { API_URL } from 'utils/config'

import Reimbursements from '../Reimbursements'

describe('src | components | pages | Reimbursements', () => {
  describe('render', () => {
    it('should display the right informations', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const downloadInformation = wrapper.find({
        children:
          'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.',
      })
      const fileFormatInformation = wrapper.find({
        children:
          'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.',
      })
      expect(downloadInformation).toHaveLength(1)
      expect(fileFormatInformation).toHaveLength(1)
    })

    it('should render a DownloadButtonContainer with the right props', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const downloadButtonContainer = wrapper.find(DownloadButtonContainer)
      expect(downloadButtonContainer).toHaveLength(1)
      expect(downloadButtonContainer.prop('filename')).toBe('remboursements_pass_culture')
      expect(downloadButtonContainer.prop('href')).toBe(`${API_URL}/reimbursements/csv`)
      expect(downloadButtonContainer.prop('mimeType')).toBe('text/csv')
      expect(downloadButtonContainer.prop('children')).toBe(
        'Télécharger la liste des remboursements'
      )
    })

    it('should render a CsvTableButton with the right props', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const displayButtonContainer = wrapper.find(DisplayButtonContainer)
      expect(displayButtonContainer).toHaveLength(1)
      expect(displayButtonContainer.prop('href')).toBe(`${API_URL}/reimbursements/csv`)
    })

    it('should display the Reimbursement Banner', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      expect(wrapper.find('Banner')).toHaveLength(1)

      const links = wrapper.find('.tertiary-link')
      expect(links).toHaveLength(2)
      expect(links.at(0).prop('href')).toBe(
        'https://aide.passculture.app/fr/articles/5096833-acteurs-culturels-quel-est-le-calendrier-des-prochains-remboursements'
      )
      expect(links.at(0).prop('children')).toContain('Les prochains remboursements')
      expect(links.at(0).find('Icon').prop('svg')).toBe('ico-external-site')

      expect(links.at(1).prop('href')).toBe(
        'https://aide.passculture.app/fr/articles/5096171-acteurs-culturels-comment-determiner-ses-modalites-de-remboursement'
      )
      expect(links.at(1).prop('children')).toContain('Les modalités de remboursements')
      expect(links.at(1).find('Icon').prop('svg')).toBe('ico-external-site')
    })
  })
})
