import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { SearchInput, type SearchInputProps } from './SearchInput'

const defaultProps: SearchInputProps = {
  label: 'Input label',
  name: 'input',
}

function renderSearchInput(props?: Partial<SearchInputProps>) {
  return render(<SearchInput {...defaultProps} {...props} />)
}

describe('SearchInput', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSearchInput()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should clear the input when clicking on the clear button', async () => {
    renderSearchInput({ value: 'test', onChange: () => {} })

    const input = screen.getByRole('searchbox', { name: 'Input label' })

    expect(input).toHaveValue('test')

    await userEvent.click(screen.getByRole('button', { name: 'Effacer' }))

    expect(input).toHaveValue('')
  })

  it('should call onChange when clearing the input', async () => {
    const handleChange = vi.fn()
    renderSearchInput({ value: 'test', onChange: handleChange })

    await userEvent.click(screen.getByRole('button', { name: 'Effacer' }))

    expect(handleChange).toHaveBeenCalled()
  })

  it('should not show the clear button when the input is disabled', () => {
    renderSearchInput({ value: 'test', onChange: () => {}, disabled: true })

    expect(
      screen.queryByRole('button', { name: 'Effacer' })
    ).not.toBeInTheDocument()
  })
})
