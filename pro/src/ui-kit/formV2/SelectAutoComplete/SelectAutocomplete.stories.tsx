import { yupResolver } from '@hookform/resolvers/yup'
import type { StoryObj } from '@storybook/react'
import { useState } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import * as yup from 'yup'

import { SelectOption } from 'commons/custom_types/form'

import { SelectAutocomplete } from './SelectAutocomplete'

// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo to work
type WrapperFormValues = { departement: string }
const FormWrapper = ({ children }: { children: React.ReactNode }) => {
  const hookForm = useForm<WrapperFormValues>({
    defaultValues: { departement: '05' },
    resolver: yupResolver(
      yup.object().shape({
        departement: yup
          .string()
          .required('Veuillez choisir un département dans la liste'),
      })
    ),
    mode: 'onTouched',
  })

  return <FormProvider {...hookForm}>{children}</FormProvider>
}

const options: SelectOption[] = [
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
]

export default {
  title: 'ui-kit/formsV2/SelectAutocomplete',
  component: SelectAutocomplete,
}

const demoStyles = {
  wrapper: {
    color: '#666',
    fontSize: '0.8rem',
    padding: '0 1rem',
    backgroundColor: '#f5f5f5',
    borderRadius: '0.2rem',
    border: 'thin solid #e1e1e1',
    minHeight: '45px',
    marginBottom: '1rem',
    display: 'flex',
    alignItems: 'center',
  },
  pre: { display: 'inline-block', padding: '0.5rem' },
}

export const Default: StoryObj<typeof SelectAutocomplete> = {
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true,
  },
}

export const NoResetOnOpen: StoryObj<typeof SelectAutocomplete> = {
  args: {
    name: 'departement',
    label: 'Département',
    options,
    isOptional: true,
    resetOnOpen: false,
    ref: (ref) => {
      if (ref) {
        ref.defaultValue = '05'
      }
      return ref
    },
  },
}

export const WithOnsearchTrigger: StoryObj<typeof SelectAutocomplete> = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [searchText, setSearchText] = useState('')

    return (
      <>
        <div style={demoStyles['wrapper']}>
          Search text value: <pre style={demoStyles['pre']}>{searchText}</pre>
        </div>

        <SelectAutocomplete
          label="Département"
          name="departement"
          options={options}
          isOptional={true}
          onSearch={(text) => setSearchText(text)}
        />
      </>
    )
  },
}

export const WithinFormValidation: StoryObj<typeof SelectAutocomplete> = {
  decorators: [
    (Story: any) => (
      <FormWrapper>
        <Story />
      </FormWrapper>
    ),
  ],
  render: () => {
    const {
      register,
      watch,
      formState: { errors },
      // eslint-disable-next-line react-hooks/rules-of-hooks
    } = useFormContext<WrapperFormValues>()

    const departement = watch('departement')

    return (
      <>
        <div style={demoStyles['wrapper']}>
          Selected value in the form:{' '}
          <pre style={demoStyles['pre']}>{departement}</pre>
        </div>

        <SelectAutocomplete
          label="Département"
          options={options}
          {...register('departement')}
          error={errors.departement?.message}
        />
      </>
    )
  },
}
