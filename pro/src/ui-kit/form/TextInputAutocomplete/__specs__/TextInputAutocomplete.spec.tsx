import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import TextInputAutocomplete from '..'
import { ITextInputAutocompleteProps } from '../TextInputAutocomplete'

const renderTextInputAutocomplete = async (
  initialValues: any,
  props: ITextInputAutocompleteProps
) => {
  await render(
    <>
      <Formik initialValues={initialValues} onSubmit={() => {}}>
        <TextInputAutocomplete {...props} />
      </Formik>
      <button type="button">Click outside ref</button>
    </>
  )
}

describe('src | ui-kit | form | TextInputAutocomplete', () => {
  let initialValues = {}
  let props: ITextInputAutocompleteProps
  const onSelectCustom = jest.fn()
  const getSuggestions = async (search: string) => {
    if (search == 'testNoSuggestions') {
      return []
    }
    return [
      {
        value: '1',
        label: `${search} - 1`,
        extraData: { postalCode: '75001' },
      },
      {
        value: '2',
        label: `${search} - 2`,
        extraData: { postalCode: '75002' },
      },
      {
        value: '3',
        label: `${search} - 3`,
        extraData: { postalCode: '75003' },
      },
      {
        value: '4',
        label: 'Option par défaut',
      },
    ]
  }
  beforeEach(() => {
    initialValues = { adresse: '', 'search-adresse': '' }
    props = {
      fieldName: 'adresse',
      label: 'Adresse',
      getSuggestions: getSuggestions,
      onSelectCustom: onSelectCustom,
    }
  })
  describe('render', () => {
    it('should display field', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      expect(screen.getByLabelText('Adresse')).toBeInTheDocument()
    })
    it('should not display any suggestions with empty search', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      expect(
        screen.queryByLabelText('Option par défaut')
      ).not.toBeInTheDocument()
    })
    it('should not display any suggestions when search not match any suggestions', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      const searchField = screen.getByLabelText('Adresse')
      await userEvent.type(searchField, 'testNoSuggestions')
      expect(
        screen.queryByLabelText('Option par défaut')
      ).not.toBeInTheDocument()
    })
    it('should display suggestions when search match suggestions', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      const searchField = screen.getByLabelText('Adresse')
      await userEvent.type(searchField, 'test')
      expect(await screen.findByText('Option par défaut')).toBeInTheDocument()
      expect(await screen.findByText('test - 1')).toBeInTheDocument()
    })
  })
  describe('select value', () => {
    it('should not set any default value for search input', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      const searchField = screen.getByLabelText('Adresse')
      expect(searchField).toHaveValue('')
    })
    it('should set input value corresponding to selected option and call custom function', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      const searchField = screen.getByLabelText('Adresse')
      await userEvent.type(searchField, 'test')
      const secondSuggestion = await screen.findByText('test - 1')
      await userEvent.click(secondSuggestion)
      expect(searchField).toHaveValue('test - 1')
      expect(onSelectCustom).toHaveBeenCalledWith({
        value: '1',
        label: 'test - 1',
        extraData: { postalCode: '75001' },
      })
    })
  })
  describe('handle on click outside', () => {
    it('set field value to last selected value on click outside', async () => {
      await renderTextInputAutocomplete(initialValues, props)
      const searchField = screen.getByLabelText('Adresse')
      await userEvent.type(searchField, 'test')
      const secondSuggestion = await screen.findByText('test - 1')
      await userEvent.click(secondSuggestion)
      expect(searchField).toHaveValue('test - 1')
      await userEvent.type(searchField, ' - not selected')
      expect(searchField).toHaveValue('test - 1 - not selected')
      const outsideSuggestionsMenuButton = await screen.findByRole('button', {
        name: 'Click outside ref',
      })
      await userEvent.click(outsideSuggestionsMenuButton)
      expect(searchField).toHaveValue('test - 1')
      expect(onSelectCustom).toHaveBeenCalledWith({
        value: '1',
        label: 'test - 1',
        extraData: { postalCode: '75001' },
      })
    })
  })
})
