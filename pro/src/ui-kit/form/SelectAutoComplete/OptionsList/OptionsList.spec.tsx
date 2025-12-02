import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createRef } from 'react'

import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { OptionsList, type OptionsListProps } from './OptionsList'

const DEFAULT_PROPS: OptionsListProps = {
  fieldName: 'departement',
  filteredOptions: [
    'Ain',
    'Aisne',
    'Allier',
    'Alpes-de-Haute-Provence',
    'Hautes-Alpes',
    'Alpes-Maritimes',
    'Ardèche',
    'Ardennes',
    'Ariège',
    'Aube',
    'Aude',
    'Aveyron',
    'Bouches-du-Rhône',
    'Calvados',
    'Cantal',
  ],
  setHoveredOptionIndex: vi.fn(),
  hoveredOptionIndex: 0,
  listRef: createRef(),
  selectOption: vi.fn(),
}

const renderOptionsList = (
  props: OptionsListProps = { ...DEFAULT_PROPS },
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OptionsList {...props} />, { ...options })
}

describe('<OptionsList />', () => {
  it('should show no results', () => {
    renderOptionsList({ ...DEFAULT_PROPS, filteredOptions: [] })

    expect(screen.getByText('Aucun résultat')).toBeInTheDocument()
  })

  it('should render list with correct ID', () => {
    renderOptionsList()
    expect(screen.getByTestId('list')).toHaveAttribute('id', 'list-departement')
  })

  it('should render options with correct data attributes', () => {
    renderOptionsList(DEFAULT_PROPS)

    const options = screen.getAllByRole('option')
    expect(options[0]).toHaveAttribute('data-value', 'Ain')
    expect(options[0]).toHaveAttribute('data-selected', 'true')
    expect(options[1]).toHaveAttribute('data-value', 'Aisne')
    expect(options[1]).toHaveAttribute('data-selected', 'false')
  })

  it('should call setHoveredOptionIndex on mouseenter and focus', async () => {
    const user = userEvent.setup()
    renderOptionsList()

    const options = screen.getAllByRole('option')
    await user.hover(options[3])
    expect(DEFAULT_PROPS.setHoveredOptionIndex).toHaveBeenCalledWith(3)

    await user.tab()
    expect(DEFAULT_PROPS.setHoveredOptionIndex).toHaveBeenCalledWith(3)
  })

  it('should call selectOption with string value on click', async () => {
    const user = userEvent.setup()
    renderOptionsList()

    const optionSpan = screen.getByText('Hautes-Alpes').closest('span')
    await user.click(optionSpan!)
    expect(DEFAULT_PROPS.selectOption).toHaveBeenCalledWith('Hautes-Alpes')
  })
})
