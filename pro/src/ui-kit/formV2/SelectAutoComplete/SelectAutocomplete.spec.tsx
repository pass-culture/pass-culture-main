import { fireEvent, render, screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { searchPatternInOptions } from 'commons/utils/searchPatternInOptions'

import {
  SelectAutocomplete,
  SelectAutocompleteProps,
} from './SelectAutocomplete'

Element.prototype.scrollIntoView = vi.fn()

describe('SelectAutocomplete', () => {
  const props: SelectAutocompleteProps = {
    label: 'Département',
    name: 'departement',
    options: [
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
    searchInOptions: searchPatternInOptions,
  }

  it('should display field', () => {
    render(<SelectAutocomplete {...props} />)
    expect(screen.getByLabelText('Département *')).toBeInTheDocument()
  })

  it('should toggle the options panel', async () => {
    render(<SelectAutocomplete {...props} />)
    await userEvent.type(screen.getByLabelText('Département *'), ' ')

    await userEvent.click(
      screen.getByRole('img', { name: 'Masquer les options' })
    )
    expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('img', { name: 'Afficher les options' })
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
      await userEvent.click(screen.getByLabelText('Département *'))
      expect(screen.getByTestId('list').children).toHaveLength(15)
    })

    it('should close and hide all options when the user triggers the close arrow button', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByLabelText('Département *'))
      await userEvent.click(
        screen.getByRole('img', { name: 'Masquer les options' })
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
      await userEvent.click(screen.getByLabelText('Département *'))
      await userEvent.click(
        await screen.findByRole('button', { name: 'Outside' })
      )
      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should replace single option', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.click(screen.getByLabelText('Département *'))
      const list = screen.getByTestId('list')
      await userEvent.click(await within(list).findByText('Aveyron'))
      expect(screen.queryByTestId('select')).toHaveValue('12')
    })
  })

  describe('filter', () => {
    it('should filter options when the user types in the field', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByLabelText('Département *'), 'al')
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
      await userEvent.type(screen.getByLabelText('Département *'), 'al')
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
      await userEvent.type(
        screen.getByLabelText('Département *'),
        'pas dans la liste'
      )
      expect(await screen.findByText(/Aucun résultat/)).toBeInTheDocument()
    })
  })

  describe('keys', () => {
    it('should close the options panel when the Tab key is pressed', async () => {
      render(<SelectAutocomplete {...props} />)
      await userEvent.type(screen.getByLabelText('Département *'), ' ')
      expect(screen.getByTestId('list').children).toHaveLength(15)
      await userEvent.tab()

      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should close the options panel when the Escape key is pressed', async () => {
      render(<SelectAutocomplete {...props} />)
      const inputContainer = screen.getByLabelText('Département *')
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
      await userEvent.click(screen.getByLabelText('Département *'))

      expect(screen.getByTestId('list').children).toHaveLength(15)

      const user = userEvent.setup()
      await user.keyboard('{ArrowDown}{ArrowDown}{ArrowUp}{ArrowDown}')
      await user.keyboard('{Enter}')

      expect(screen.getByLabelText('Département *')).toHaveValue('Aisne')
    })
  })

  it('should call "onChange" and "onBlur" when user selects a valid option', async () => {
    const onBlur = vi.fn()
    const onChange = vi.fn()

    render(
      <SelectAutocomplete {...props} onChange={onChange} onBlur={onBlur} />
    )
    const user = userEvent.setup()

    const input = screen.getByLabelText('Département *')
    await user.type(input, 'Aisne')

    const option = (
      await screen.findByRole('option', { name: 'Aisne' })
    ).querySelector('span')
    await user.click(option!)

    expect(onChange).toHaveBeenCalledWith({
      type: 'change',
      target: { name: 'departement', value: '02' },
    })
    expect(onBlur).toHaveBeenCalledWith({
      type: 'blur',
      target: { name: 'departement', value: '02' },
    })
  })

  it('should call "onBlur" with an empty value when user types an invalid value', async () => {
    const onBlur = vi.fn()
    const onChange = vi.fn()

    render(
      <SelectAutocomplete {...props} onChange={onChange} onBlur={onBlur} />
    )
    const user = userEvent.setup()

    const input = screen.getByLabelText('Département *')
    await user.type(input, 'Paris')
    await user.tab()

    expect(onBlur).toHaveBeenCalledWith({
      type: 'blur',
      target: { name: 'departement', value: '' },
    })
    expect(onChange).toHaveBeenCalled()
  })

  it('should not clear the input on focus if "resetOnOpen" is false', async () => {
    render(
      <SelectAutocomplete
        {...{
          ...props,
          resetOnOpen: false,
          onReset: undefined,
          ref: (ref) => {
            if (ref) {
              ref.defaultValue = '02'
            }
            return ref
          },
        }}
      />
    )
    await userEvent.click(screen.getByLabelText('Département *'))

    expect(screen.getByLabelText('Département *')).toHaveValue('Aisne')
  })
})
