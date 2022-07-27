import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import SelectAutocomplete, {
  SelectAutocompleteProps,
} from '../SelectAutocomplete'

describe('src | ui-kit | form | SelectAutocomplete', () => {
  describe('render', () => {
    const props: SelectAutocompleteProps = {
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
    }
    const initialValues = { departement: '' }

    it('should display field', () => {
      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <SelectAutocomplete {...props} />
        </Formik>
      )
      expect(screen.getByLabelText('Département')).toBeInTheDocument()
    })

    describe('Options', () => {
      it('should not display options at first display', () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        expect(screen.queryByLabelText('Ain')).not.toBeInTheDocument()
        expect(screen.queryByLabelText('Cantal')).not.toBeInTheDocument()
      })

      it('should open and display all options when the user focuses on the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        expect(await screen.findAllByRole('option')).toHaveLength(15)
      })

      it('should close and hide all options when the user triggers the close arrow button', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(screen.getByAltText('Masquer les options'))
        expect(screen.queryAllByRole('role')).toHaveLength(0)
      })

      it('should close and hide options when the user focuses outside of the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <>
              <button>Outside</button>
              <SelectAutocomplete {...props} />
            </>
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(
          await screen.findByRole('button', { name: 'Outside' })
        )
        expect(screen.queryAllByRole('option')).toHaveLength(0)
      })

      it('should display selected option in the text input when the user selects it', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        await userEvent.click(await screen.findByLabelText('Aveyron'))
        expect(screen.getByRole('textbox')).toHaveValue('Aveyron')
      })

      it('should display disabled option', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} maxDisplayOptions={5} />
          </Formik>
        )
        await userEvent.click(screen.getByRole('textbox'))
        const additionalOption = await screen.findByLabelText(
          /5 résultats maximum. Veuillez affiner votre recherche/
        )
        expect(additionalOption).toBeDisabled()
      })
    })

    describe('Filter', () => {
      it('should filter options when the user types in the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.type(screen.getByRole('textbox'), 'al')
        expect(screen.getAllByRole('option')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal

        await userEvent.clear(screen.getByRole('textbox'))
        await userEvent.type(screen.getByRole('textbox'), 'bouches rhon')
        expect(screen.getAllByRole('option')).toHaveLength(1) // Bouches-du-Rhône
      })

      it('should reset filter when the user closes the field', async () => {
        render(
          <Formik initialValues={initialValues} onSubmit={() => {}}>
            <SelectAutocomplete {...props} />
          </Formik>
        )
        await userEvent.type(screen.getByRole('textbox'), 'al')
        expect(screen.getAllByRole('option')).toHaveLength(6) // Allier, Alpes, Hautes-Alpes, Alpes-Maritimes, Calvados, Cantal
        await userEvent.click(screen.getByAltText('Masquer les options'))
        await userEvent.click(screen.getByAltText('Afficher les options'))
        expect(screen.getAllByRole('option')).toHaveLength(15)
      })
    })

    it('should display an error when input value is not valid for Formik', async () => {
      const validationSchema = yup.object().shape({
        departement: yup.array().required('Veuillez renseigner un département'),
        'search-departement': yup
          .string()
          .when('departement', (departement, schema) =>
            schema.test({
              name: 'search-departement-invalid',
              message: 'error',
              test: departement ? () => false : () => true,
            })
          ),
      })
      render(
        <Formik
          initialValues={initialValues}
          onSubmit={() => {}}
          validationSchema={validationSchema}
        >
          <SelectAutocomplete {...props} />
        </Formik>
      )
      expect(
        screen.queryByText('Veuillez renseigner un Département')
      ).not.toBeInTheDocument()
      await userEvent.click(screen.getByRole('textbox'))
      await userEvent.click(screen.getByAltText('Masquer les options'))
      await waitFor(() => {
        expect(
          screen.queryByText('Veuillez renseigner un département')
        ).toBeInTheDocument()
      })
    })
  })
})
