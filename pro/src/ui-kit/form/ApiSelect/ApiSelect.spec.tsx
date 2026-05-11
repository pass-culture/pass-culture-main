import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { type ApiOption, ApiSelect, type ApiSelectProps } from './ApiSelect'

const name = 'any-name'
const apiSelectLabel = 'any-label'

const mockValue = 'option-value'
const mockOnSelect = vi.fn()
const mockSearchApi = vi.fn()
const mockOnCreate = vi.fn()
const mockOnReset = vi.fn()

const renderApiSelect = (props?: Partial<ApiSelectProps<ApiOption>>) => {
  return render(
    <ApiSelect
      name={name}
      label={apiSelectLabel}
      onSelect={mockOnSelect}
      searchApi={mockSearchApi}
      onCreate={mockOnCreate}
      onReset={mockOnReset}
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
    expect(screen.getByText('option-label')).toBeInTheDocument()
  })

  it('should not fetch options if search is too short', async () => {
    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'op')

    expect(mockSearchApi).not.toHaveBeenCalled()

    expect(screen.getByText('Aucun résultat')).toBeInTheDocument()
  })

  it('should add creatable option', async () => {
    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'creatable')

    expect(screen.getByText('Ajouter "creatable"')).toBeInTheDocument()
  })

  it('should not add creatable option if value is too short', async () => {
    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'cr')

    expect(screen.queryByText(/Ajouter/)).not.toBeInTheDocument()
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

  it('should create new option', async () => {
    renderApiSelect()

    await userEvent.type(screen.getByLabelText(/any-label/), 'creatable')

    const creatableOption = await screen.findByRole('option', {
      name: /Ajouter creatable/,
    })
    await userEvent.click(creatableOption)

    expect(mockOnCreate).toHaveBeenCalledWith('creatable')
  })

  it('should not fail when api fail', async () => {
    mockSearchApi.mockRejectedValueOnce([])

    renderApiSelect()
    await userEvent.type(screen.getByLabelText(/any-label/), 'Lucie Aubrac')
    expect(
      await screen.findByText('Ajouter "Lucie Aubrac"')
    ).toBeInTheDocument()
  })

  it('should search options on mount', async () => {
    renderApiSelect({ value: mockValue })

    await waitFor(() => {
      expect(mockSearchApi).toHaveBeenCalledWith(mockValue)
    })
  })

  it('should reset form value when value is empty', async () => {
    renderApiSelect({ value: mockValue })

    const input = screen.getByLabelText(/any-label/)
    await userEvent.clear(input)

    expect(mockOnReset).toHaveBeenCalled()
  })

  it('should fallback on current form value on blur event when value is not empty', async () => {
    mockSearchApi.mockResolvedValueOnce([
      {
        value: 'option-value',
        label: 'option-label',
        thumbUrl: 'option-thumbUrl',
      },
    ])
    renderApiSelect({ value: mockValue })

    await waitFor(() => expect(mockSearchApi).toHaveBeenCalledWith(mockValue))

    const input = screen.getByLabelText(/any-label/)
    await userEvent.type(input, 'new-option-label')
    fireEvent.blur(input)

    await waitFor(() => expect(input).toHaveValue('option-label'))
  })
})
