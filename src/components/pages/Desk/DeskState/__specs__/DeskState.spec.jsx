import { shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'
import React from 'react'

import { formatLocalTimeDateString } from '../../../../../utils/timezone'
import DeskState from '../DeskState'

jest.mock('../../../../../utils/timezone', () => ({
  formatLocalTimeDateString: jest.fn(),
}))
describe('src | components | pages | Desk | DeskState ', () => {
  let props

  beforeEach(() => {
    props = {
      booking: {
        offerName: 'fake offer',
        userName: 'fake user name',
        venueDepartementCode: '93',
      },
      message: 'fake message',
      level: 'fake level',
    }
  })

  describe('render', () => {
    it('should render a DeskState component with the proper information from props', () => {
      // when
      const wrapper = shallow(<DeskState {...props} />)

      // then
      const table = wrapper.find('table')
      const lines = table.find('tr')
      expect(lines).toHaveLength(3)
      expect(
        lines
          .at(0)
          .find('th')
          .text()
      ).toBe('Utilisateur :')
      expect(
        lines
          .at(0)
          .find('td')
          .text()
      ).toBe('fake user name')
      expect(
        lines
          .at(1)
          .find('th')
          .text()
      ).toBe('Offre :')
      expect(
        lines
          .at(1)
          .find('td')
          .text()
      ).toBe('fake offer')
      expect(
        lines
          .at(2)
          .find('th')
          .text()
      ).toBe('Date de l’offre :')
      expect(
        lines
          .at(2)
          .find('td')
          .text()
      ).toBe('Permanent')
    })

    it('should display empty label for offer date when no booking', () => {
      // given
      props.booking = null

      // when
      const wrapper = shallow(<DeskState {...props} />)

      // then
      const table = wrapper.find('table')
      const lines = table.find('tr')
      expect(
        lines
          .at(2)
          .find('td')
          .text()
      ).toBe('')
    })

    it('should display a formatted date label for offer when booking date is given', () => {
      // given
      props.booking.date = '2019/01/01'
      formatLocalTimeDateString.mockReturnValue('fake date')

      // when
      const wrapper = shallow(<DeskState {...props} />)

      // then
      const table = wrapper.find('table')
      const lines = table.find('tr')
      expect(formatLocalTimeDateString).toHaveBeenCalledWith('2019/01/01', '93')
      expect(
        lines
          .at(2)
          .find('td')
          .text()
      ).toBe('fake date')
    })

    it('should display an Icon for validation and use the right css class when level is success', () => {
      // given
      props.level = 'success'

      // when
      const wrapper = shallow(<DeskState {...props} />)

      // then
      const icon = wrapper.find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('svg')).toBe('picto-validation')
      expect(
        wrapper
          .find('div')
          .at(1)
          .prop('className')
      ).toBe('state success')
    })

    it('should display an Icon for failure and use the right css class when level is error', () => {
      // given
      props.level = 'error'

      // when
      const wrapper = shallow(<DeskState {...props} />)

      // then
      const icon = wrapper.find('.state').find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('svg')).toBe('picto-echec')
      expect(
        wrapper
          .find('div')
          .at(1)
          .prop('className')
      ).toBe('state error')
    })
  })
})
