import { render, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { searchPatternInOptions } from 'utils/searchPatternInOptions'

import SelectAutocomplete, {
  SelectAutocompleteProps,
} from '../SelectAutocomplete'

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
        label: 'Alpes-de-Haute-Provence test libellé très long',
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
    pluralLabel: 'Départements',
    searchInOptions: searchPatternInOptions,
  }
  const initialValues = { departement: '01', 'search-departement': '' }

  it('should display field', () => {
    render(
      <Formik initialValues={initialValues} onSubmit={vi.fn()}>
        <SelectAutocomplete {...props} />
      </Formik>
    )
    expect(screen.getByLabelText('Département')).toBeInTheDocument()
  })

  describe('Options', () => {
    it('should not display options at first display', () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      expect(screen.queryByLabelText('Ain')).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Cantal')).not.toBeInTheDocument()
    })

    it('should open and display all options when the user focuses on the field', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.click(screen.getByLabelText('Département'))
      expect(screen.getByTestId('list').children).toHaveLength(15)
    })

    it('should close and hide all options when the user triggers the close arrow button', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.click(screen.getByLabelText('Département'))
      await userEvent.click(
        screen.getByRole('img', { name: 'Masquer les options' })
      )
      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })

    it('should close and hide options when the user focuses outside of the field', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <>
            <button>Outside</button>
            <SelectAutocomplete {...props} />
          </>
        </Formik>
      )
      await userEvent.click(screen.getByLabelText('Département'))
      await userEvent.click(
        await screen.findByRole('button', { name: 'Outside' })
      )
      expect(screen.queryByTestId('list')).not.toBeInTheDocument()
    })
    describe('Multi', () => {
      it('should display the number of selected options', async () => {
        render(
          <Formik
            initialValues={{
              departement: ['01', '02'],
              'search-departement': '',
            }}
            onSubmit={vi.fn()}
          >
            <SelectAutocomplete {...{ ...props, multi: true }} />
          </Formik>
        )
        expect(await screen.findByText('2')).toBeInTheDocument()
      })
      it('should select several options', async () => {
        render(
          <Formik
            initialValues={{
              departement: ['01', '02'],
              'search-departement': '',
            }}
            onSubmit={vi.fn()}
          >
            <SelectAutocomplete {...{ ...props, multi: true }} />
          </Formik>
        )
        await userEvent.click(screen.getByLabelText('Département'))
        const list = screen.getByTestId('list')
        await userEvent.click(await within(list).findByText('Aveyron'))
        await userEvent.click(await within(list).findByText('Calvados'))
        expect(screen.queryByTestId('select')).toHaveValue([
          '01', // Ain (initial value)
          '02', // Aisne (initial value)
          '12', // Aveyron
          '14', // Calvados
        ])
      })

      it('should unselect options', async () => {
        render(
          <Formik
            initialValues={{
              departement: ['01', '02'],
              'search-departement': '',
            }}
            onSubmit={vi.fn()}
          >
            <SelectAutocomplete {...{ ...props, multi: true }} />
          </Formik>
        )
        await userEvent.click(screen.getByLabelText('Département'))
        const list = screen.getByTestId('list')
        await userEvent.click(await within(list).findByText('Ain'))
        expect(screen.queryByTestId('select')).toHaveValue([
          '02', // Aisne (initial value)
        ])
      })
    })

    describe('Simple', () => {
      it('should replace single option', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={vi.fn()}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByLabelText('Département'))
        const list = screen.getByTestId('list')
        await userEvent.click(await within(list).findByText('Aveyron'))
        expect(screen.queryByTestId('select')).toHaveValue('12')
      })
    })
  })

  describe('filter', () => {
    it('should filter options when the user types in the field', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.type(screen.getByLabelText('Département'), 'al')
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

    it('should reset filter when the user closes and reopens the field', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.type(screen.getByLabelText('Département'), 'al')
      await userEvent.click(
        screen.getByRole('img', { name: 'Masquer les options' })
      )
      await userEvent.click(
        screen.getByRole('img', { name: 'Afficher les options' })
      )

      expect(screen.getByTestId('list').children).toHaveLength(15)
    })

    it('should warn that there are no results', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={vi.fn()}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.type(
        screen.getByLabelText('Département'),
        'pas dans la liste'
      )
      expect(await screen.findByText(/Aucun résultat/)).toBeInTheDocument()
    })
  })

  describe('tags', () => {
    it('should display tags when the user selects options', async () => {
      render(
        <Formik
          initialValues={{
            departement: ['01', '02'],
            'search-departement': '',
          }}
          onSubmit={vi.fn()}
        >
          <SelectAutocomplete {...{ ...props, multi: true }} />
        </Formik>
      )
      await userEvent.click(screen.getByLabelText('Département'))
      const list = screen.getByTestId('list')
      await userEvent.click(await within(list).findByText('Aveyron'))
      await userEvent.click(await within(list).findByText('Calvados'))
      expect(
        screen.getByRole('button', { name: /Aveyron/ })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Calvados/ })
      ).toBeInTheDocument()
    })

    it('should not display associated tags when tags are hidden and the user selects options', async () => {
      render(
        <Formik
          initialValues={{
            departement: ['01', '02'],
            'search-departement': '',
          }}
          onSubmit={vi.fn()}
        >
          <SelectAutocomplete {...{ ...props, multi: true }} hideTags />
        </Formik>
      )
      await userEvent.click(screen.getByLabelText('Département'))
      const list = screen.getByTestId('list')
      await userEvent.click(await within(list).findByText('Aveyron'))
      await userEvent.click(await within(list).findByText('Calvados'))
      expect(
        screen.queryByRole('button', { name: /Aveyron/ })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: /Calvados/ })
      ).not.toBeInTheDocument()
    })

    it('should remove a tag when the user closes the tag', async () => {
      render(
        <Formik
          initialValues={{
            departement: ['01', '02'],
            'search-departement': '',
          }}
          onSubmit={vi.fn()}
        >
          <SelectAutocomplete {...{ ...props, multi: true }} />
        </Formik>
      )

      await userEvent.click(screen.getByRole('button', { name: /Aisne/ }))
      expect(
        screen.queryByRole('button', { name: 'Aisne' })
      ).not.toBeInTheDocument()
    })
    it('should unselect option when the user removes a tag', async () => {
      render(
        <Formik
          initialValues={{
            departement: ['01', '02'],
            'search-departement': '',
          }}
          onSubmit={vi.fn()}
        >
          <SelectAutocomplete {...{ ...props, multi: true }} />
        </Formik>
      )
      await userEvent.click(screen.getByRole('button', { name: /Aisne/ }))
      await userEvent.click(screen.getByLabelText('Département'))
      // Ain (01) still selected, Aisne (02) not selected any more
      expect(screen.queryByTestId('select')).toHaveValue(['01'])
    })
  })

  it('should display an error when input value is not valid for Formik', async () => {
    const validationSchema = yup.object().shape({
      departement: yup.array().test({
        message: 'Veuillez renseigner un département',
        test: items => Boolean(items?.length && items.length > 0),
      }),
    })
    render(
      <Formik
        initialValues={{ departement: ['01', '02'], 'search-departement': '' }}
        onSubmit={() => {}}
        validationSchema={validationSchema}
      >
        <SelectAutocomplete {...{ ...props, multi: true }} />
      </Formik>
    )
    await userEvent.click(screen.getByLabelText('Département'))
    // when user unselects default options
    const list = screen.getByTestId('list')
    await userEvent.click(await within(list).findByText('Ain'))
    await userEvent.click(await within(list).findByText('Aisne'))
    await waitFor(() => {
      expect(
        screen.getByText(/Veuillez renseigner un département/)
      ).toBeInTheDocument()
    })
  })

  it('should clear the input on focus', async () => {
    render(
      <Formik
        initialValues={{
          departement: ['01', '02'],
          'search-departement': 'Test search',
        }}
        onSubmit={vi.fn()}
      >
        <SelectAutocomplete {...{ ...props, multi: true }} />
      </Formik>
    )
    await userEvent.click(screen.getByLabelText('Département'))

    expect(screen.getByLabelText('Département')).toHaveValue('')
  })

  it('should not clear the input on focus', async () => {
    render(
      <Formik
        initialValues={{
          departement: ['01', '02'],
          'search-departement': 'Test search',
        }}
        onSubmit={vi.fn()}
      >
        <SelectAutocomplete
          {...{ ...props, multi: true, resetOnOpen: false }}
        />
      </Formik>
    )
    await userEvent.click(screen.getByLabelText('Département'))

    expect(screen.getByLabelText('Département')).toHaveValue('Test search')
  })
})
