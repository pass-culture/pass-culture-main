import { shallow } from 'enzyme'
import React from 'react'

import Icon from 'components/layout/Icon'

import TableHead from '../TableHead'

describe('components | pages | TableWrapper | TableHead', () => {
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
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
            },
            {
              id: 2,
              headerTitle: 'Beneficiaires',
              render: jest.fn(() => <span>Beneficiaires</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    expect(wrapper.find('th')).toHaveLength(2)
    expect(wrapper.find('th').at(0).text()).toBe('Offres')
    expect(wrapper.find('th').at(1).text()).toBe('Beneficiaires')
  })

  it('should return no line when there is no headers', () => {
    // Given
    const props = {
      headerGroups: [],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    expect(wrapper.find('tr')).toHaveLength(0)
  })

  it('should render one line with default sorting icon when column is sortable', () => {
    // Given
    const props = {
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
              canSort: true,
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    const firstColumn = wrapper.find('th')
    expect(firstColumn).toHaveLength(1)
    expect(firstColumn.find({ children: 'Offres' })).toHaveLength(1)
    const defaultSortingIcon = firstColumn.find(Icon)
    expect(defaultSortingIcon).toHaveLength(1)
    expect(defaultSortingIcon.prop('svg')).toBe('ico-unfold')
  })

  it('should render one line with no default sorting icon when column is not sortable', () => {
    // Given
    const props = {
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
              canSort: false,
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    const firstColumn = wrapper.find('th')
    expect(firstColumn).toHaveLength(1)
    expect(firstColumn.find({ children: 'Offres' })).toHaveLength(1)
    const defaultSortingIcon = firstColumn.find(Icon)
    expect(defaultSortingIcon).toHaveLength(0)
  })

  it('should render one line with icon sorted ASC when column is sorted by ASC', () => {
    // Given
    const props = {
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
              canSort: true,
              isSorted: true,
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    const firstColumn = wrapper.find('th')
    expect(firstColumn).toHaveLength(1)
    expect(firstColumn.find({ children: 'Offres' })).toHaveLength(1)
    const defaultSortingIcon = firstColumn.find(Icon)
    expect(defaultSortingIcon).toHaveLength(1)
    expect(defaultSortingIcon.prop('svg')).toBe('ico-arrow-down-r')
  })

  it('should render one line with icon sorted DESC when column is sorted by DESC', () => {
    // Given
    const props = {
      headerGroups: [
        {
          id: 1,
          headers: [
            {
              id: 1,
              headerTitle: 'Offres',
              render: jest.fn(() => <span>Offres</span>),
              getHeaderProps: jest.fn(),
              getSortByToggleProps: jest.fn(),
              canSort: true,
              isSorted: true,
              isSortedDesc: true,
            },
          ],
        },
      ],
    }

    // When
    const wrapper = shallow(<TableHead {...props} />)

    // Then
    const firstColumn = wrapper.find('th')
    expect(firstColumn).toHaveLength(1)
    expect(firstColumn.find({ children: 'Offres' })).toHaveLength(1)
    const defaultSortingIcon = firstColumn.find(Icon)
    expect(defaultSortingIcon).toHaveLength(1)
    expect(defaultSortingIcon.prop('svg')).toBe('ico-arrow-up-r')
  })
})
