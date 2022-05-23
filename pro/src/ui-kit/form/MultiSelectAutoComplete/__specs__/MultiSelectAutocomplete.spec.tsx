import '@testing-library/jest-dom'

import MultiSelectAutocomplete, {
  MultiSelectAutocompleteProps,
} from '../MultiSelectAutocomplete'
import { render, screen, waitFor } from '@testing-library/react'

import { Formik } from 'formik'
import React from 'react'
import userEvent from '@testing-library/user-event'

describe('src | components | layout | Banner', () => {
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
      await userEvent.click(screen.getByRole('button'))

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
      await userEvent.click(screen.getByRole('button'))
      // and reopens it
      await userEvent.click(screen.getByRole('button'))
      // then
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox')).toHaveLength(15)
      })
    })

    it('should add options when the user selects them', async () => {
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
    })
  })
})
