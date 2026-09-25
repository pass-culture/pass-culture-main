import type { AccessibilityFormValues } from '@/commons/core/shared/types'

export type NfdOfferFormOption = {
  value: string
  label: string
}

export type NfdOfferFormField = {
  type: string
  required: boolean
  label: string
  options: NfdOfferFormOption[]
}

export type NfdOfferFormSection = {
  id: string
  title: string
  fields: NfdOfferFormField[]
}

export type NfdOfferFormResponse = {
  nature: string
  domain: string
  formDefinition: NfdOfferFormSection[]
  name: string
  description: string
  accessibility: AccessibilityFormValues
}

export type NfdOfferFormValues = {
  name: string
  description: string
  accessibility: AccessibilityFormValues
}
