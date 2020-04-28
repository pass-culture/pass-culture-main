import { shallow } from 'enzyme'
import React from 'react'

import BankFields from '../BankFields'
import TextField from '../../../../../../layout/form/fields/TextField'

describe('src | components | pages | Venue | fields | BankFields', () => {
  let props

  beforeEach(() => {
    props = {
      adminUserOfferer: true,
      areBankInformationProvided: false,
      readOnly: true,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<BankFields {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should display information label when user is not admin of the offerer', () => {
      // given
      props.adminUserOfferer = false

      // when
      const wrapper = shallow(<BankFields {...props} />)

      // then
      const title = wrapper.find('h2 > span')
      expect(title.text()).toBe(
        "Vous avez besoin d'être administrateur de la structure pour éditer ces informations."
      )
    })

    it('should not display information label when user is admin of the offerer', () => {
      // given
      props.adminUserOfferer = true

      // when
      const wrapper = shallow(<BankFields {...props} />)

      // then
      const title = wrapper.find('h2 > span')
      expect(title.text()).toBe('')
    })

    it('should display two TextField components with the right props', () => {
      // when
      const wrapper = shallow(<BankFields {...props} />)

      // then
      const textFields = wrapper.find(TextField)
      expect(textFields).toHaveLength(2)
      expect(textFields.at(0).prop('label')).toBe('BIC : ')
      expect(textFields.at(0).prop('name')).toBe('bic')
      expect(textFields.at(0).prop('readOnly')).toBe(true)
      expect(textFields.at(1).prop('label')).toBe('IBAN : ')
      expect(textFields.at(1).prop('name')).toBe('iban')
      expect(textFields.at(1).prop('readOnly')).toBe(true)
    })

    it('should render a label element with text containing instructions for offerer when bic/iban are missing', () => {
      // given
      props.areBankInformationProvided = false

      // when
      const wrapper = shallow(<BankFields {...props} />)

      // then
      const labelElement = wrapper.find('p')
      expect(labelElement.prop('className')).toBe('bank-instructions-label fs13')
      expect(labelElement.text()).toBe(
        'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
      )
    })

    it('should not render a label element with text containing instructions for offerer when bic/iban are provided', () => {
      // given
      props.areBankInformationProvided = true

      // when
      const wrapper = shallow(<BankFields {...props} />)

      // then
      const labelElement = wrapper.find('p')
      expect(labelElement).toHaveLength(0)
    })
  })
})
