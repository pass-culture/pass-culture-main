import { shallow } from 'enzyme'
import React from 'react'

import DisplayButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import { API_URL } from 'utils/config'

import Reimbursements from '../Reimbursements'

describe('src | components | pages | Reimbursements', () => {
  describe('render', () => {
    it('should a Main component with the right props', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      expect(wrapper.prop('name')).toBe('reimbursements')
    })

    it('should display the right informations', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const downloadInformation = wrapper.find({
        children: 'Téléchargez le récapitulatif des remboursements de vos offres.',
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
  })
})
