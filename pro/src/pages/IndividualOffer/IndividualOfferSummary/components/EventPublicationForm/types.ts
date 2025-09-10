export type EventPublicationFormValues = {
  publicationMode: 'now' | 'later'
  publicationDate?: string
  publicationTime?: string
  bookingAllowedMode: 'now' | 'later'
  bookingAllowedDate?: string
  bookingAllowedTime?: string
}
