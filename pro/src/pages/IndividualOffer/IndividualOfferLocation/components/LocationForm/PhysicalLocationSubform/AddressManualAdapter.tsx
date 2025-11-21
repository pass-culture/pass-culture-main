import { useEffect, useRef } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import type { AddressFormValues } from '@/commons/core/shared/types'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'

import type {
  LocationFormValues,
  PhysicalAddressSubformValues,
} from '../../../commons/types'
import { PhysicalLocationValidationSchema } from '../../../commons/utils/getValidationSchema'

const PHYSICAL_LOCATION_MANUAL_ADDRESS_FIELDS: (keyof PhysicalAddressSubformValues)[] =
  ['street', 'postalCode', 'city', 'coords']

interface AddressManualAdapterProps {
  readOnlyFields?: string[]
  gpsCalloutMessage?: string
}
/**
 * Adapter that lets the shared (flat) AddressManual component work with nested address.* form values
 * without modifying the shared component or rolling back the new nested structure.
 */
export const AddressManualAdapter = ({
  readOnlyFields,
  gpsCalloutMessage,
}: AddressManualAdapterProps) => {
  const isSyncingRef = useRef(false)

  const form = useFormContext<LocationFormValues>()
  const address = form.watch('location')

  const addressManualSubform = useForm<AddressFormValues>({
    defaultValues: {
      street: address?.street,
      postalCode: address?.postalCode,
      city: address?.city,
      latitude: address?.latitude,
      longitude: address?.longitude,
      coords: address?.coords ?? undefined,
    },
  })

  // Lift up changes from AddressManual subform to main Location form
  useEffect(() => {
    const subscription = addressManualSubform.watch((value, { name }) => {
      if (!name || isSyncingRef.current) {
        return
      }

      if (name in PhysicalLocationValidationSchema.fields) {
        form.setValue(`location.${name}` as const, value[name] ?? '', {
          shouldDirty: true,
          shouldTouch: true,
        })
      }
    })

    return () => subscription.unsubscribe()
  }, [addressManualSubform, form])

  // Pass down updated values from main Location form to AddressManual subform
  useEffect(() => {
    isSyncingRef.current = true

    addressManualSubform.reset({
      street: address?.street || '',
      postalCode: address?.postalCode || '',
      city: address?.city || '',
      coords: address?.coords || '',
      latitude: address?.latitude || '',
      longitude: address?.longitude || '',
    })

    setTimeout(() => {
      isSyncingRef.current = false
    }, 0)
  }, [address, addressManualSubform])

  // Pass down validation errors from main Location form to AddressManual subform
  useEffect(() => {
    const addressErrors = form.formState.errors.location
    if (!addressErrors) {
      return
    }

    PHYSICAL_LOCATION_MANUAL_ADDRESS_FIELDS.forEach((field) => {
      const fieldError = addressErrors[field]

      if (fieldError?.message) {
        addressManualSubform.setError(field as keyof AddressFormValues, {
          type: 'manual',
          message: fieldError.message,
        })
      } else {
        addressManualSubform.clearErrors(field as keyof AddressFormValues)
      }
    })
  }, [form.formState.errors.location, addressManualSubform])

  return (
    <FormProvider {...addressManualSubform}>
      <AddressManual
        readOnlyFields={readOnlyFields}
        gpsCalloutMessage={gpsCalloutMessage}
      />
    </FormProvider>
  )
}
