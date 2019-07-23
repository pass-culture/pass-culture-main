import React from 'react'
import { shallow } from 'enzyme'

import Reimbursements from '../Reimbursements'
import HeroSection from '../../../layout/HeroSection/HeroSection'
import DownloadButtonContainer from '../../../layout/DownloadButton/DownloadButtonContainer'
import { API_URL } from '../../../../utils/config'
import DisplayButtonContainer from '../../../layout/CsvTableButton/CsvTableButtonContainer'

describe('src | components | pages | Reimbursements', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should a Main component with the right props', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      expect(wrapper.prop('name')).toBe('reimbursements')
    })

    it('should render a HeroSection containing two paragraphs with the right information', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const heroSection = wrapper.find(HeroSection)
      expect(heroSection).toHaveLength(1)
      expect(heroSection.prop('title')).toBe('Suivi des remboursements')
      const paragraphs = heroSection.find('p')
      expect(paragraphs).toHaveLength(2)
      expect(paragraphs.at(0).prop('className')).toBe('subtitle')
      expect(paragraphs.at(0).text()).toBe(
        'Téléchargez le récapitulatif des remboursements de vos offres.'
      )
      expect(paragraphs.at(1).prop('className')).toBe('subtitle')
      expect(paragraphs.at(1).text()).toBe(
        'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'
      )
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

    it('should render a DisplayButtonContainer with the right props', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      const displayButtonContainer = wrapper.find(DisplayButtonContainer)
      expect(displayButtonContainer).toHaveLength(1)
      expect(displayButtonContainer.prop('href')).toBe(`${API_URL}/reimbursements/csv`)
    })
  })
})
