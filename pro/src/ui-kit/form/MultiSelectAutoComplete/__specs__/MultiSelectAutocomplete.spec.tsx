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

    it('should display field', () => {
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )
      expect(screen.getByLabelText('Département')).toBeInTheDocument()
    })

    it('should display the number of selected options', async () => {
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <MultiSelectAutocomplete {...props} />
        </Formik>
      )
      expect(await screen.findByText('2')).toBeInTheDocument()
    })

    describe('Options', () => {
      it('should not display options at first display', () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        expect(screen.queryByLabelText('Ain')).not.toBeInTheDocument()
        expect(screen.queryByLabelText('Cantal')).not.toBeInTheDocument()
      })

      it('should open and display all options when the user focuses on the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        expect(await screen.findAllByRole('checkbox')).toHaveLength(15)
      })

      it('should close and hide all options when the user triggers the close arrow button', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(screen.getByAltText('Masquer les options'))
        expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
      })

      it('should close and hide options when the user focuses outside of the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <>
              <button>Outside</button>
              <MultiSelectAutocomplete {...props} />
            </>
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(
          await screen.findByRole('button', { name: 'Outside' })
        )
        expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
      })

      it('should display options as selected when the user selects them', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(await screen.findByLabelText('Aveyron'))
        await userEvent.click(await screen.findByLabelText('Calvados'))
        expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(
          4
        ) // Ain, Aisne (default) + Aveyron, Calvados
        await userEvent.click(await screen.findByLabelText('Calvados'))
        expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(
          3
        ) // Ain, Aisne (default) + Aveyron
      })
    })

    describe('Filter', () => {
      it('should filter options when the user types in the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.type(screen.getByRole('textbox'), 'al')
        expect(screen.getAllByRole('checkbox')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal
      })

      it('should reset filter when the user closes the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.type(screen.getByRole('textbox'), 'al')
        expect(screen.getAllByRole('checkbox')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal
        await userEvent.click(screen.getByAltText('Masquer les options'))
        await userEvent.click(screen.getByAltText('Afficher les options'))
        expect(screen.getAllByRole('checkbox')).toHaveLength(15)
      })
    })

    describe('Tags', () => {
      it('should display tags when the user selects options', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(await screen.findByLabelText('Aveyron'))
        await userEvent.click(await screen.findByLabelText('Calvados'))
        expect(
          screen.getByRole('button', { name: 'Aveyron' })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('button', { name: 'Calvados' })
        ).toBeInTheDocument()
      })

      it('should not display associated tags when the user selects options', async () => {
        // given
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} hideTags />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(await screen.findByLabelText('Aveyron'))
        await userEvent.click(await screen.findByLabelText('Calvados'))
        expect(
          screen.queryByRole('button', { name: 'Aveyron' })
        ).not.toBeInTheDocument()
        expect(
          screen.queryByRole('button', { name: 'Calvados' })
        ).not.toBeInTheDocument()
      })

      it('should unselect option when removing a tag', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <MultiSelectAutocomplete {...props} />
          </Formik>
        )

        await userEvent.click(screen.getByRole('button', { name: 'Aisne' }))
        expect(
          screen.queryByRole('button', { name: 'Aisne' })
        ).not.toBeInTheDocument()
        await userEvent.click(screen.getByRole('textbox'))
        expect(screen.queryByLabelText('Aisne')).not.toBeChecked()
      })
    })

    it('should display an error when input value is not valid for Formik', async () => {
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
      expect(
        screen.queryByText('Veuillez renseigner un Département')
      ).not.toBeInTheDocument()
      await userEvent.click(screen.getByRole('textbox'))
      // and unselects default options
      await userEvent.click(await screen.findByLabelText('Ain'))
      await userEvent.click(await screen.findByLabelText('Aisne'))
      await waitFor(() => {
        expect(
          screen.queryByText('Veuillez renseigner un département')
        ).toBeInTheDocument()
      })
    })
  })
})
