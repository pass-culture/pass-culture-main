import '@testing-library/jest-dom'

import * as yup from 'yup'

import MultiSelectAutocomplete, {
  MultiSelectAutocompleteProps,
} from '../MultiSelectAutocomplete'
import { render, screen, waitFor } from '@testing-library/react'

import { Formik } from 'formik'
import React from 'react'
import userEvent from '@testing-library/user-event'

describe('src | ui-kit | form | MutliSelectAutocomplete', () => {
  describe('render', () => {
    const props: MultiSelectAutocompleteProps = {
      label: 'Département',
      fieldName: 'departement',
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
    }
    const initialValues = { departement: ['01', '02'] }

    it('should not display options by default', () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // then
      expect(screen.queryByLabelText('Ain')).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Cantal')).not.toBeInTheDocument()
    })

    it('should display all options when the user opens the field', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )

      // then
      expect(await screen.findAllByRole('checkbox')).toHaveLength(15)
    })

    it('should hide all options when the user closes the field', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and then closes it
      await userEvent.click(screen.getByAltText('Masquer les options'))

      // then
      expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
    })

    it('should hide options when the user clicks outside of the field', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <>
            <button>Outside</button>
            <MultiSelectAutocomplete {...props} />
          </>
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and clicks outside of the field
      await userEvent.click(
        await screen.findByRole('button', { name: 'Outside' })
      )

      // then
      await waitFor(() => {
        expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
      })
    })

    it('should filter options when the user types in the field', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // when the user types in the field
      await userEvent.type(
        screen.getByRole('textbox', { name: 'Département' }),
        'al'
      )

      // then
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal
      })
    })

    it('should cancel filter when the user closes the field', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )
      await userEvent.type(
        screen.getByRole('textbox', { name: 'Département' }),
        'al'
      )
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal
      })
      // when the user closes the field
      await userEvent.click(screen.getByAltText('Masquer les options'))
      // and reopens it
      await userEvent.click(screen.getByAltText('Afficher les options'))
      // then
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox')).toHaveLength(15)
      })
    })

    it('should add options when the user selects them and display associated tags', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and selects options
      await userEvent.click(await screen.findByLabelText('Aveyron'))
      await userEvent.click(await screen.findByLabelText('Calvados'))

      // then
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(
          4
        ) // Ain, Aisne (default) + Aveyron, Calvados
      })
      expect(
        screen.queryByRole('button', { name: 'Aveyron' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Calvados' })
      ).toBeInTheDocument()
    })

    it('should add options when the user selects them but not display associated tags', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} hideTags={true} />
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and selects options
      await userEvent.click(await screen.findByLabelText('Aveyron'))
      await userEvent.click(await screen.findByLabelText('Calvados'))

      // then
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(
          4
        ) // Ain, Aisne (default) + Aveyron, Calvados
      })
      expect(
        screen.queryByRole('button', { name: 'Aveyron' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Calvados' })
      ).not.toBeInTheDocument()
    })

    it('should remove options when the user unselects them', async () => {
      // given
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and unselects default options
      await userEvent.click(await screen.findByLabelText('Ain'))
      await userEvent.click(await screen.findByLabelText('Aisne'))

      // then
      await waitFor(() => {
        expect(
          screen.queryAllByRole('checkbox', { checked: true })
        ).toHaveLength(0)
      })
      expect(
        screen.queryByRole('button', { name: 'Aveyron' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Calvados' })
      ).not.toBeInTheDocument()
    })

    it('should display an error when input value is not valid for Formik', async () => {
      // given
      const validationSchema = yup.object().shape({
        departement: yup.array().test({
          message: 'Veuillez renseigner un département',
          test: domains => Boolean(domains?.length && domains.length > 0),
        }),
        'search-departement': yup
          .string()
          .when('departement', (departements, schema) =>
            schema.test({
              name: 'search-departement-invalid',
              message: 'error',
              test: departements.length === 0 ? () => false : () => true,
            })
          ),
      })
      render(
        <Formik
          initialValues={initialValues}
          onSubmit={() => {}}
          validationSchema={validationSchema}
        >
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )

      expect(screen.queryByTestId('error-departement')).not.toBeInTheDocument()

      // when the user opens the field
      await userEvent.click(
        screen.getByRole('textbox', { name: 'Département' })
      )
      // and unselects default options
      await userEvent.click(await screen.findByLabelText('Ain'))
      await userEvent.click(await screen.findByLabelText('Aisne'))

      // then
      await waitFor(() => {
        expect(screen.queryByTestId('error-departement')).toBeInTheDocument()
      })
    })
  })
})
