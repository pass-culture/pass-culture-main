import { fireEvent, render, screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { searchPatternInOptions } from '@/commons/utils/searchPatternInOptions'

import {
  SelectAutocomplete,
  type SelectAutocompleteProps,
} from './SelectAutocomplete'

Element.prototype.scrollIntoView = vi.fn()

describe('SelectAutocomplete', () => {
  const props: SelectAutocompleteProps = {
    label: 'Département',
    name: 'departement',
    options: [
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
    searchInOptions: searchPatternInOptions,
  }

  it('should render without accessibility violations', async () => {
    const { container } = render(<SelectAutocomplete {...props} />)

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should display field', () => {
    render(<SelectAutocomplete {...props} />)
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('should toggle the options panel', async () => {
    render(<SelectAutocomplete {...props} />)
    await userEvent.type(screen.getByRole('combobox'), ' ')

    await userEvent.click(
      screen.getByRole('button', { name: 'Masquer les options' })
    )
    expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Afficher les options' })
    )

    expect(screen.getByTestId('list').children).toHaveLength(15)
  })

  describe('Options', () => {
    it('should not display options at first display', () => {
      render(<SelectAutocomplete {...props} />)
      expect(screen.queryByLabelText('Ain')).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Cantal')).not.toBeInTheDocument()
    })

    it('should open and display all options when the user focuses on the field', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByRole('combobox'))
      expect(screen.getByTestId('list').children).toHaveLength(15)
    })

    it('should close and hide all options when the user triggers the close arrow button', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByRole('combobox'))
      await userEvent.click(
        screen.getByRole('button', { name: 'Masquer les options' })
      )
      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should close and hide options when the user focuses outside of the field', async () => {
      render(
        <>
          <button>Outside</button>
          <SelectAutocomplete {...props} />
        </>
      )
      await userEvent.click(screen.getByRole('combobox'))
      await userEvent.click(
        await screen.findByRole('button', { name: 'Outside' })
      )
      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should replace single option', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByRole('combobox'))
      const list = screen.getByTestId('list')
      await userEvent.click(await within(list).findByText('Aveyron'))
      expect(screen.queryByRole('combobox')).toHaveValue('Aveyron')
    })
  })

  describe('filter', () => {
    it('should filter options when the user types in the field', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByRole('combobox'), 'al')
      expect(screen.getByTestId('list').children).toHaveLength(
        [
          'Allier',
          'Alpes',
          'Hautes-Alpes',
          'Alpes-Maritimes',
          'Calvados',
          'Cantal',
        ].length
      )
    })

    it('should filter options with the default filter function when the user types in the field ', async () => {
      const propsWithoutFilterFunction = { ...props }
      delete propsWithoutFilterFunction.searchInOptions

      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByRole('combobox'), 'al')
      expect(screen.getByTestId('list').children).toHaveLength(
        [
          'Allier',
          'Alpes',
          'Hautes-Alpes',
          'Alpes-Maritimes',
          'Calvados',
          'Cantal',
        ].length
      )
    })

    it('should warn that there are no results', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByRole('combobox'), 'pas dans la liste')
      expect(await screen.findByText(/Aucun résultat/)).toBeInTheDocument()
    })
  })

  describe('keys', () => {
    it('should close the options panel when the Tab key is pressed', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByRole('combobox'), ' ')
      expect(screen.getByTestId('list').children).toHaveLength(15)
      await userEvent.tab()

      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should close the options panel when the Escape key is pressed', async () => {
      render(<SelectAutocomplete {...props} />)
      const inputContainer = screen.getByRole('combobox')
      await userEvent.type(inputContainer, ' ')
      expect(screen.getByTestId('list').children).toHaveLength(15)
      fireEvent.keyDown(inputContainer, {
        key: 'Escape',
        code: 'Escape',
        keyCode: 27,
        charCode: 27,
      })

      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should browse through the options with the keyboard when dropdown is open', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByRole('combobox'))

      expect(screen.getByTestId('list').children).toHaveLength(15)

      const user = userEvent.setup()
      await user.keyboard('{ArrowDown}{ArrowDown}{ArrowUp}{ArrowDown}')
      await user.keyboard('{Enter}')

      expect(screen.getByRole('combobox')).toHaveValue('Aisne')
    })
  })

  it('should call "onBlur" when user selects a valid option', async () => {
    const onBlur = vi.fn()
    const onChange = vi.fn()

    render(
      <SelectAutocomplete {...props} onChange={onChange} onBlur={onBlur} />
    )
    const user = userEvent.setup()

    const input = screen.getByRole('combobox')
    await user.type(input, 'Aisne')

    const option = (
      await screen.findByRole('option', { name: 'Aisne' })
    ).querySelector('span')
    await user.click(option!)

    expect(onBlur).toHaveBeenCalledWith({
      type: 'blur',
      target: { name: 'departement', value: 'Aisne' },
    })
  })

  it('should call "onBlur" when user tabs out of the field', async () => {
    const onBlur = vi.fn()
    const onChange = vi.fn()

    render(
      <SelectAutocomplete {...props} onChange={onChange} onBlur={onBlur} />
    )
    const user = userEvent.setup()

    const input = screen.getByRole('combobox')
    await user.type(input, 'Paris')
    await user.tab()

    expect(onBlur).toHaveBeenCalledWith({
      type: 'blur',
      target: { name: 'departement', value: 'Paris' },
    })
    expect(onChange).toHaveBeenCalled()
  })

  it('should not clear the input on focus if "resetOnOpen" is false', async () => {
    render(
      <SelectAutocomplete
        {...{
          ...props,
          value: 'Aisne',
          resetOnOpen: false,

          ref: (ref) => {
            if (ref) {
              ref.defaultValue = 'Aisne'
            }
            return ref
          },
        }}
      />
    )
    await userEvent.click(screen.getByRole('combobox'))

    expect(screen.getByRole('combobox')).toHaveValue('Aisne')
  })
})
