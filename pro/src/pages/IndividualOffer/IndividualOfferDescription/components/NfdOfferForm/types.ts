import type { AccessibilityFormValues } from '@/commons/core/shared/types'

export type NfdOfferFormResponse = {
  nature: string
  domain: string
  capabilities: string[]
  mandatoryFields: string[]
  name: string
  description: string
  accessibility: AccessibilityFormValues
}

export type NfdOfferFormValues = {
  name: string
  description: string
  accessibility: AccessibilityFormValues
}
