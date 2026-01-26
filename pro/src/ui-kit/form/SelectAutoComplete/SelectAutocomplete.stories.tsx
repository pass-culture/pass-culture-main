import { yupResolver } from '@hookform/resolvers/yup'
import type { StoryObj } from '@storybook/react-vite'
import { type PropsWithChildren, useState } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import * as yup from 'yup'

import type { SelectOption } from '@/commons/custom_types/form'

import { SelectAutocomplete } from './SelectAutocomplete'

// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo to work
type WrapperFormValues = { departement: string }
const FormWrapper = ({ children }: PropsWithChildren) => {
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
  { value: '01', label: 'Ain', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '02', label: 'Aisne'},
  { value: '03', label: 'Allier', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  {
    value: '04',
    label: 'Alpes-de-Haute-Provence test de libellé très long', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"
  },
  { value: '05', label: 'Hautes-Alpes', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '06', label: 'Alpes-Maritimes' , thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '07', label: 'Ardèche', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '08', label: 'Ardennes', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '09', label: 'Ariège', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '10', label: 'Aube', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '11', label: 'Aude', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '12', label: 'Aveyron', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '13', label: 'Bouches-du-Rhône', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '14', label: 'Calvados', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
  { value: '15', label: 'Cantal', thumbUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Arbre_%C3%A0.jpg/640px-Arbre_%C3%A0.jpg"},
]

export default {
  title: '@/ui-kit/forms/SelectAutocomplete',
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
    required: false,
    shouldResetOnOpen: true,
  },
}

export const NoResetOnOpen: StoryObj<typeof SelectAutocomplete> = {
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
    shouldResetOnOpen: false,
    value: '05',
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
          required={false}
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
