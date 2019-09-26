import React from 'react'
import { shallow } from 'enzyme'
import ModificationControl from '../ModificationControl'

describe('src | components | pages | Offerer | ModificationControl ', () => {
  let props

  beforeEach(() => {
    props = {
      parseFormChild: a => {
        return a
      },
      offerer: {
        id: 'TgJ764rtd',
      },
      query: {
        context: jest.fn().mockReturnValue({
          readOnly: true,
        }),
      },
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<ModificationControl {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('when readonly and  offerer is admin', () => {
      it('should render a modify link', () => {
        // given
        props.adminUserOfferer = true
        const wrapper = shallow(<ModificationControl {...props} />)

        // when
        const navLink = wrapper.find('NavLink')

        // then
        expect(navLink.props().to).toBe('/structures/TgJ764rtd?modification')
        expect(navLink.props().children[0]).toBe('Modifier les informations')
      })
    })

    describe('when not in readOnly', () => {
      it('should render a modify link', () => {
        // given
        jest.spyOn(props.query, 'context').mockReturnValue({
          readOnly: false,
        })
        const wrapper = shallow(<ModificationControl {...props} />)

        // when
        const navLink = wrapper.find('NavLink')
        const cancelButton = wrapper.find('CancelButton')
        const submitButton = wrapper.find('SubmitButton')

        // then
        expect(navLink).toHaveLength(0)
        expect(cancelButton.props().to).toBe('/structures/TgJ764rtd')
        expect(cancelButton.props().children[0]).toBe('Annuler')
        expect(submitButton.props().children[0]).toBe('Valider')
      })
    })
  })
})
