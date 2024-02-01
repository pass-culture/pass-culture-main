import { StoryObj } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import MultiSelectAutocomplete from './MultiSelectAutocomplete'
import type { MultiSelectAutocompleteProps } from './MultiSelectAutocomplete'

export default {
  title: 'ui-kit/forms/MultiSelectAutocomplete',
  component: MultiSelectAutocomplete,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{ departement: ['01', '02'], 'search-departement': '' }}
        onSubmit={() => {}}
      >
        <Story />
      </Formik>
    ),
  ],
}

const defaultProps: MultiSelectAutocompleteProps = {
  pluralLabel: 'Départements',
  name: 'departement',
  options: [
    { value: '01', label: 'Ain' },
    { value: '02', label: 'Aisne' },
    { value: '03', label: 'Allier' },
    {
      value: '04',
      label: 'Alpes-de-Haute-Provence test de libellé très long',
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
  label: 'Département',
  hideFooter: false,
  hideTags: false,
  isOptional: false,
  smallLabel: false,
}

export const Default: StoryObj<typeof MultiSelectAutocomplete> = {
  args: { ...defaultProps },
}

export const WithoutTags: StoryObj<typeof MultiSelectAutocomplete> = {
  args: { ...defaultProps, hideTags: true },
}
