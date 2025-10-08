import { render } from '@testing-library/react'
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
})
