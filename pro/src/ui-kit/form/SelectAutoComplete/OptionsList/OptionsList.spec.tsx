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
    { value: '01', label: 'Ain' },
    { value: '02', label: 'Aisne' },
    { value: '03', label: 'Allier' },
    {
      value: '04',
      label: 'Alpes-de-Haute-Provence',
    },
    { value: '05', label: 'Hautes-Alpes' },
    { value: '06', label: 'Alpes-Maritimes' },
    { value: '07', label: 'Ardèche' },
    { value: '08', label: 'Ardennes' },
    { value: '09', label: 'Ariège' },
    { value: '10', label: 'Aube' },
    { value: '11', label: 'Aude' },
    { value: '12', label: 'Aveyron' },
    { value: '13', label: 'Bouches-du-Rhône' },
    { value: '14', label: 'Calvados' },
    { value: '15', label: 'Cantal' },
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
    expect(options[0]).toHaveAttribute('data-value', '01')
    expect(options[0]).toHaveAttribute('data-selected', 'true')
    expect(options[1]).toHaveAttribute('data-value', '02')
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

  it('should call selectOption with options on click', async () => {
    const user = userEvent.setup()
    renderOptionsList()

    const optionSpan = screen.getByText('Hautes-Alpes').closest('span')
    await user.click(optionSpan!)
    expect(DEFAULT_PROPS.selectOption).toHaveBeenCalledWith({
      value: '05',
      label: 'Hautes-Alpes',
    })
  })

  it('should render option thumbnails when thumbPlaceholder is provided', () => {
    renderOptionsList({
      ...DEFAULT_PROPS,
      thumbPlaceholder: '/placeholder.png',
    })

    const imgs = screen.getAllByRole('presentation', { hidden: true })
    expect(imgs).toHaveLength(15)
    expect(imgs[0]).toHaveAttribute('src', '/placeholder.png')
  })

  it('should use thumbUrl when provided', () => {
    const optionsWithThumbUrl = [
      { value: '01', label: 'Ain', thumbUrl: 'https://example.com/ain.jpg' },
    ]
    renderOptionsList({
      ...DEFAULT_PROPS,
      filteredOptions: optionsWithThumbUrl,
      thumbPlaceholder: '/placeholder.png',
    })

    const img = screen.getByRole('presentation', { hidden: true })
    expect(img).toHaveAttribute('src', 'https://example.com/ain.jpg')
  })

  it('should use thumbPlaceholder when thumbUrl fails to load', () => {
    const optionsWithThumbUrl = [
      { value: '01', label: 'Ain', thumbUrl: 'https://example.com/ain.jpg' },
    ]
    renderOptionsList({
      ...DEFAULT_PROPS,
      filteredOptions: optionsWithThumbUrl,
      thumbPlaceholder: '/placeholder.png',
    })

    const img = screen.getByRole('presentation', { hidden: true })
    img.dispatchEvent(new Event('error'))
    expect(img).toHaveAttribute('src', '/placeholder.png')
  })
})
