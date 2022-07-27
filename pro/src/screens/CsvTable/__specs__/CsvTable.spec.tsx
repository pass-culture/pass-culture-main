import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as csvService from 'routes/CsvTable/adapters/getCsvData'
import { configureTestStore } from 'store/testUtils'

import CsvTable, { ICsvTableProps } from '../CsvTable'
import { ITableData } from '../types'

interface ICsvTableTestProps {
  getCsvData: jest.SpyInstance<Promise<ITableData | null>>
}

// FIXME: we don't have store type yet.
// This will be irrelevant soon as we are removing it
const renderCsvTable = async ({
  props,
  storeOverride = {},
}: {
  props: ICsvTableTestProps
  storeOverride?: any
}) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <CsvTable {...(props as unknown as ICsvTableProps)} />
      </MemoryRouter>
    </Provider>
  )
}

const getCsvDataMock = jest.spyOn(csvService, 'getCsvData')

describe('src | components | layout | CsvTable', () => {
  let dataFromCsv: ITableData
  let props: ICsvTableTestProps

  beforeEach(() => {
    dataFromCsv = {
      data: [
        ['data1', 'data2'],
        ['data3', 'data4'],
      ],
      headers: ['column1', 'column2'],
    }

    props = {
      getCsvData: getCsvDataMock.mockResolvedValue(dataFromCsv),
    }
  })

  describe('render', () => {
    it('should render a CsvTable component with a spinner, then a message with no data when there is an error', async () => {
      props.getCsvData.mockRejectedValue(null)
      renderCsvTable({ props })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })

    it('should render a CsvTable component with a spinner, then a message with no data when there is no data', async () => {
      props.getCsvData.mockResolvedValue({ ...dataFromCsv, data: [] })
      renderCsvTable({ props })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(
          screen.getByText(/Il n’y a pas de données à afficher/)
        ).toBeInTheDocument()
      })
    })

    it('should render a CsvTable component with a spinner, then a table with the data', async () => {
      renderCsvTable({ props })

      expect(screen.getByText('Chargement en cours')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.getAllByRole('columnheader')).toHaveLength(2)
      })
      expect(screen.getAllByRole('cell')).toHaveLength(4)
    })

    it('should open a new window for printing when clicking on print button', async () => {
      renderCsvTable({ props })

      jest.spyOn(global, 'print').mockImplementation()
      fireEvent.click(await screen.findByText('Imprimer'))

      expect(global.print).toHaveBeenCalledTimes(1)
    })
  })
})
