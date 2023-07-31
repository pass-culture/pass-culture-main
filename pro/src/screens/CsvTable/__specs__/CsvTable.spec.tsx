import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { vi, expect } from 'vitest'

import { renderWithProviders } from 'utils/renderWithProviders'

import CsvTable, { CsvTableProps } from '../CsvTable'

const renderCsvTable = (props: CsvTableProps) =>
  renderWithProviders(<CsvTable {...props} />)

describe('src | components | layout | CsvTable', () => {
  describe('render', () => {
    it('should render a CsvTable component with a spinner, then a message with no data when there is an error', async () => {
      const mockGetCsvData = vi.fn().mockResolvedValueOnce(null)
      renderCsvTable({ getCsvData: mockGetCsvData })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })

    it('should render a CsvTable component with a spinner, then a message with no data when there is no data', async () => {
      const getCsvDataMock = vi.fn().mockResolvedValueOnce({
        data: [],
        headers: ['column1', 'column2'],
      })
      renderCsvTable({ getCsvData: getCsvDataMock })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })

    it('should render a CsvTable component with a spinner, then a table with the data', async () => {
      const getCsvDataMock = vi.fn().mockResolvedValueOnce({
        data: [
          ['data1', 'data2'],
          ['data3', 'data4'],
        ],
        headers: ['column1', 'column2'],
      })
      renderCsvTable({ getCsvData: getCsvDataMock })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getAllByRole('columnheader')).toHaveLength(2)
      })
      expect(screen.getAllByRole('cell')).toHaveLength(4)
    })
  })
})
