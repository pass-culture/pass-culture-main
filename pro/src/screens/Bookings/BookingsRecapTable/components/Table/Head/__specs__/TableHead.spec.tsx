import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import TableHead, { TableHeadProps } from '../TableHead'

describe('TableHead', () => {
  const renderHead = <
    T extends BookingRecapResponseModel | CollectiveBookingResponseModel
  >(
    props: TableHeadProps<T>
  ) => {
    return render(<TableHead {...props} />, {
      container: document.body.appendChild(document.createElement('table')),
    })
  }
  it('should render one line with all columns', () => {
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

    // @ts-expect-error we do not mock all react table props,
    // this code should be refactored to remove react-table so I don't do it now
    renderHead(props)

    expect(screen.getAllByRole('columnheader')).toHaveLength(2)
    expect(screen.getAllByRole('columnheader')[0]).toHaveTextContent('Offres')
    expect(screen.getAllByRole('columnheader')[1]).toHaveTextContent(
      'Beneficiaires'
    )
  })

  it('should return no line when there is no headers', async () => {
    const props = {
      headerGroups: [],
    }

    renderHead(props)

    expect(screen.queryByRole('row')).not.toBeInTheDocument()
  })

  it('should render one line with sorting icons when column is sortable', () => {
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

    // @ts-expect-error we do not mock all react table props,
    // this code should be refactored to remove react-table so I don't do it now
    renderHead(props)

    expect(
      screen.getByRole('img', { name: 'Trier par ordre croissant' })
    ).toBeInTheDocument()
  })
})
