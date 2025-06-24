import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { searchPatternInOptions } from 'commons/utils/searchPatternInOptions'

import {
  SelectAutocomplete,
  SelectAutocompleteProps,
} from './SelectAutocomplete'

const ComponentWithFormik = (args: Args) => (
  <Formik initialValues={args.initialValues} onSubmit={() => {}}>
    <SelectAutocomplete {...args} />
  </Formik>
)

export default {
  title: 'ui-kit/forms/SelectAutocomplete',
  component: ComponentWithFormik,
}
interface Args extends SelectAutocompleteProps {
  initialValues: {
    departement: string | string[]
    'search-departement': string
  }
}

const defaultProps: Args = {
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
  initialValues: { departement: '01', 'search-departement': '' },
  label: 'Département',
  hideTags: false,
  isOptional: false,
  searchInOptions: searchPatternInOptions,
}

export const Default: StoryObj<typeof ComponentWithFormik> = {
  args: { ...defaultProps },
}

export const Multi: StoryObj<typeof ComponentWithFormik> = {
  args: {
    ...defaultProps,
    multi: true,
    initialValues: { departement: ['01', '02'], 'search-departement': '' },
  },
}

export const WithoutTags: StoryObj<typeof ComponentWithFormik> = {
  args: {
    ...defaultProps,
    multi: true,
    initialValues: { departement: ['01', '02'], 'search-departement': '' },
    hideTags: true,
  },
}
