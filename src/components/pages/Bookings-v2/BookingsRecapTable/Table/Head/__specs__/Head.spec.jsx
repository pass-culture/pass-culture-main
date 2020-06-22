import React from 'react'
import { shallow } from 'enzyme'
import Head from '../Head'

describe('components | pages | Table | Head', () => {
  it('should render one line with all columns', () => {
    // Given
    const props = {
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => (
                <span>
                  {'Offres'}
                </span>
              )),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
            },
            {
              id: 2,
              headerTitle: 'Beneficiaires',
              render: jest.fn(() => (
                <span>
                  {'Beneficiaires'}
                </span>
              )),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<Head {...props} />)

    // Then
    expect(wrapper.find('th')).toHaveLength(2)
    expect(
      wrapper
        .find('th')
        .at(0)
        .text()
    ).toBe('Offres')
    expect(
      wrapper
        .find('th')
        .at(1)
        .text()
    ).toBe('Beneficiaires')
  })

  it('should return no line when there is no headers', () => {
    // Given
    const props = {
      headerGroups: [],
    }

    // When
    const wrapper = shallow(<Head {...props} />)

    // Then
    expect(wrapper.find('tr')).toHaveLength(0)
  })
})
