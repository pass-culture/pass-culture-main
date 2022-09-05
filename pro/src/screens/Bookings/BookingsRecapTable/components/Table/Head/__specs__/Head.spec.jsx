import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

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
    render(<TableHead {...props} />)

    // Then

    expect(screen.getAllByRole('columnheader')).toHaveLength(2)
    expect(screen.getAllByRole('columnheader')[0]).toHaveTextContent('Offres')
    expect(screen.getAllByRole('columnheader')[1]).toHaveTextContent(
      'Beneficiaires'
    )
  })

  it('should return no line when there is no headers', async () => {
    // Given
    const props = {
      headerGroups: [],
    }

    // When
    render(<TableHead {...props} />)

    // Then
    expect(await screen.queryByRole('row')).not.toBeInTheDocument()
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
    render(<TableHead {...props} />)
    // Then
    expect(screen.getByRole('button')).toHaveAttribute(
      'src',
      expect.stringContaining('ico-unfold')
    )
  })

  it('should render one line with no default sorting icon when column is not sortable', async () => {
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
    render(<TableHead {...props} />)

    // Then
    expect(screen.getByRole('columnheader')).toHaveTextContent('Offres')
    expect(await screen.queryByRole('button')).not.toBeInTheDocument()
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
    render(<TableHead {...props} />)

    // Then
    expect(screen.getByRole('columnheader')).toHaveTextContent('Offres')
    expect(screen.getByRole('button')).toHaveAttribute(
      'src',
      expect.stringContaining('ico-arrow-down-r')
    )
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
    render(<TableHead {...props} />)

    // Then
    expect(screen.getByRole('columnheader')).toHaveTextContent('Offres')
    expect(screen.getByRole('button')).toHaveAttribute(
      'src',
      expect.stringContaining('ico-arrow-up-r')
    )
  })
})
