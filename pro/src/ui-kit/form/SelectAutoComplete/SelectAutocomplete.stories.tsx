import { yupResolver } from '@hookform/resolvers/yup'
import type { StoryObj } from '@storybook/react-vite'
import { type PropsWithChildren, useState } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import * as yup from 'yup'


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

const options: string[] = [
  'Ain',  
  'Aisne',    
  'Allier',
  'Alpes-de-Haute-Provence test de libellé très long',
 'Hautes-Alpes',
  'Alpes-Maritimes',
  'Ardèche',
 'Ardennes',
  'Ariège',
  'Aube',
  'Aude',
  'Aveyron',
  'Bouches-du-Rhône',
  'Calvados',
  'Cantal',
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
  },
}

export const NoResetOnOpen: StoryObj<typeof SelectAutocomplete> = {
  args: {
    name: 'departement',
    label: 'Département',
    options,
    required: false,
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
          onChange={(event) => {
            setSearchText(event.target.value)
          }}
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
