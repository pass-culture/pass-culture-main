import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { ApiSelect, type ApiSelectProps } from './ApiSelect'

const name = 'any-name'
const apiSelectLabel = 'any-label'

const mockOnSelect = vi.fn()
const mockSearchApi = vi.fn()
const mockOnSearch = vi.fn()

const renderApiSelect = (props?: Partial<ApiSelectProps>) => {
  return render(
    <ApiSelect
      name={name}
      label={apiSelectLabel}
      onSelect={mockOnSelect}
      searchApi={mockSearchApi}
      onSearch={mockOnSearch}
      {...props}
    />
  )
}

describe('ApiSelect', () => {
  it('should pass a11y tests', async () => {
    const { container } = renderApiSelect()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should fetch options', async () => {
    mockSearchApi.mockResolvedValueOnce([
      {
        value: 'option-value',
        label: 'option-label',
        thumbUrl: 'option-thumbUrl',
      },
    ])

    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'option')

    await waitFor(() => {
      expect(mockSearchApi).toHaveBeenCalledWith('option')
    })
    expect(mockOnSearch).toHaveBeenCalledWith('option')
    expect(screen.getByText('option-label')).toBeInTheDocument()
  })

  it('should not fetch options if search is too short', async () => {
    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'op')

    expect(mockSearchApi).not.toHaveBeenCalled()

    expect(screen.getByText('Aucun résultat')).toBeInTheDocument()
  })

  it('should select options', async () => {
    mockSearchApi.mockResolvedValueOnce([
      {
        value: 'option-value',
        label: 'option-label',
        thumbUrl: 'option-thumbUrl',
      },
    ])

    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'option')

    await waitFor(() => {
      expect(screen.getByText('option-label')).toBeInTheDocument()
    })

    await userEvent.click(screen.getByText('option-label'))
    expect(screen.getByLabelText(/any-label/)).toHaveValue('option-label')

    expect(mockOnSelect).toHaveBeenCalledWith({
      value: 'option-value',
      label: 'option-label',
      thumbUrl: 'option-thumbUrl',
    })
  })

  it('should not fail when api fail', async () => {
    mockSearchApi.mockRejectedValueOnce([])

    renderApiSelect()
    await userEvent.type(screen.getByLabelText(/any-label/), 'Lucie Aubrac')
    expect(await screen.findByText('Aucun résultat')).toBeInTheDocument()
  })

  it('should search options on mount', async () => {
    renderApiSelect({ value: 'option-value' })

    await waitFor(() => {
      expect(mockSearchApi).toHaveBeenCalledWith('option-value')
    })
  })
})
