import { yupResolver } from '@hookform/resolvers/yup'
import { Meta, StoryObj } from '@storybook/react'
import { CSSProperties, PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'
import * as yup from 'yup'

import { AddressSelect } from './AddressSelect'

export default {
  title: '@/ui-kit/formsV2/AddressSelect',
  component: AddressSelect,
} as Meta<typeof AddressSelect>

const demoStyles: Record<string, CSSProperties> = {
  wrapper: {
    color: '#666',
    fontSize: '0.8rem',
    padding: '1rem',
    backgroundColor: '#f5f5f5',
    borderRadius: '0.2rem',
    border: 'thin solid #e1e1e1',
    minHeight: '45px',
    marginBottom: '1rem',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
  },
  pre: { display: 'inline-block', padding: '0.5rem' },
}

type AddressFormValues = {
  addressText: string
  street: string
  postalCode: string
  city: string
  latitude: string
  longitude: string
  inseeCode: string
  banId: string
}
// <FormWrapper> provides a react-hook-form context, which is necessary for the storybook demo to work
const FormWrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<AddressFormValues>({
    defaultValues: {
      addressText: '19 Rue de Toulouse 30000 Nîmes',
      street: '19 Rue de Toulouse',
      postalCode: '30000',
      city: 'Nîmes',
      latitude: '43.828539',
      longitude: '4.375801',
      inseeCode: '30000',
      banId: '30189_7810_00019',
    },
    resolver: yupResolver(
      yup.object().shape({
        addressText: yup
          .string()
          .required('Veuillez sélectionner une adresse valide'),
        street: yup.string().default(''),
        postalCode: yup.string().default(''),
        city: yup.string().default(''),
        latitude: yup.string().default(''),
        longitude: yup.string().default(''),
        inseeCode: yup.string().default(''),
        banId: yup.string().default(''),
      })
    ),
    mode: 'onBlur',
  })

  const [
    street,
    city,
    postalCode,
    latitude,
    longitude,
    addressText,
    inseeCode,
    banId,
  ] = hookForm.watch([
    'street',
    'city',
    'postalCode',
    'latitude',
    'longitude',
    'addressText',
    'inseeCode',
    'banId',
  ])

  return (
    <FormProvider {...hookForm}>
      <div style={demoStyles['wrapper']}>
        Selected value in the form: <br />
        <pre style={demoStyles['pre']}>
          addressText = {addressText}
          <br />
          street = {street}
          <br />
          city = {city}
          <br />
          postalCode = {postalCode}
          <br />
          latitude = {latitude}
          <br />
          longitude = {longitude}
          <br />
          inseeCode = {inseeCode}
          <br />
          banId = {banId}
        </pre>
      </div>
      <form>{children}</form>
    </FormProvider>
  )
}

export const Default: StoryObj<typeof AddressSelect> = {
  args: {
    name: 'addressText',
    label: 'Adresse postale',
  },
}

export const withLimitOf15Suggestions: StoryObj<typeof AddressSelect> = {
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    suggestionLimit: 15,
    ref: (ref) => {
      if (ref) {
        ref.defaultValue = '8 Rue'
      }
      return ref
    },
  },
}

export const Disabled: StoryObj<typeof AddressSelect> = {
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    disabled: true,
  },
}

export const optionalWithDescription: StoryObj<typeof AddressSelect> = {
  args: {
    name: 'addressText',
    label: 'Adresse postale',
    description: 'Uniquement si vous souhaitez préciser l’adresse exacte',
    isOptional: true,
  },
}

export const onlyMunicipality: StoryObj<typeof AddressSelect> = {
  args: {
    name: 'cityName',
    label: 'Nom de la ville',
    onlyTypes: ['municipality'],
    value: 'Noisy',
    suggestionLimit: 50,
  },
}

export const WithinFormValidation: StoryObj<typeof AddressSelect> = {
  decorators: [
    (Story: any) => (
      <FormWrapper>
        <Story />
      </FormWrapper>
    ),
  ],
  render: () => {
    const {
      setValue,
      register,
      formState: { errors },
      // eslint-disable-next-line react-hooks/rules-of-hooks
    } = useFormContext<AddressFormValues>()

    return (
      <AddressSelect
        label="Adresse postale"
        {...register('addressText')}
        error={errors.addressText?.message}
        onAddressChosen={(addressData) => {
          setValue('street', addressData.address)
          setValue('postalCode', addressData.postalCode)
          setValue('city', addressData.city)
          setValue('latitude', String(addressData.latitude))
          setValue('longitude', String(addressData.longitude))
          setValue('banId', addressData.id)
          setValue('inseeCode', addressData.inseeCode)
        }}
      />
    )
  },
}
