import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as csvService from 'routes/CsvTable/adapters/getCsvData'
import { configureTestStore } from 'store/testUtils'

import CsvTable from '../CsvTable'

describe('src | components | layout | CsvTable', () => {
  const dataFromCsv = {
    data: [
      ['data1', 'data2'],
      ['data3', 'data4'],
    ],
    headers: ['column1', 'column2'],
  }
  const stubStore = configureTestStore()
  describe('render', () => {
    it('should render a CsvTable component with a spinner, then a message with no data when there is an error', async () => {
      jest.spyOn(csvService, 'getCsvData').mockRejectedValue(null)
      // when
      render(
        <Provider store={stubStore}>
          <MemoryRouter>
            <CsvTable getCsvData={csvService.getCsvData} />
          </MemoryRouter>
        </Provider>
      )
      // then
      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      // and
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })
    it('should render a CsvTable component with a spinner, then a message with no data when there is no data', async () => {
      jest
        .spyOn(csvService, 'getCsvData')
        .mockResolvedValue({ ...dataFromCsv, data: [] })
      // when
      render(
        <Provider store={stubStore}>
          <MemoryRouter>
            <CsvTable getCsvData={csvService.getCsvData} />
          </MemoryRouter>
        </Provider>
      )
      // then
      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      // and
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })
    it('should render a CsvTable component with a spinner, then a table with the data', async () => {
      jest.spyOn(csvService, 'getCsvData').mockResolvedValue(dataFromCsv)
      // when
      render(
        <Provider store={stubStore}>
          <MemoryRouter>
            <CsvTable getCsvData={csvService.getCsvData} />
          </MemoryRouter>
        </Provider>
      )
      // then
      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      // and
      await waitFor(() => {
        expect(screen.getAllByRole('columnheader')).toHaveLength(2)
      })
      expect(screen.getAllByRole('cell')).toHaveLength(4)
    })
    it('should open a new window for printing when clicking on print button', async () => {
      jest.spyOn(csvService, 'getCsvData').mockResolvedValue(dataFromCsv)
      // given
      jest.spyOn(global, 'print').mockImplementation()
      render(
        <Provider store={stubStore}>
          <MemoryRouter>
            <CsvTable getCsvData={csvService.getCsvData} />
          </MemoryRouter>
        </Provider>
      )
      // when
      fireEvent.click(await screen.findByText(/Imprimer/))
      // then
      expect(global.print).toHaveBeenCalledTimes(1)
    })
  })
})
