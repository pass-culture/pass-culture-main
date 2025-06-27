export type EventPublicationEditionFormValues = {
  publicationMode: 'now' | 'later' | null
  publicationDate?: string
  publicationTime?: string
  bookingAllowedMode: 'now' | 'later' | null
  bookingAllowedDate?: string
  bookingAllowedTime?: string
  isPaused: boolean
}
