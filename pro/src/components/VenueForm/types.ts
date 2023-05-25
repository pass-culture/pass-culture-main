import { IAccessibiltyFormValues } from 'core/shared'

import { VenueBannerMetaProps } from './ImageUploaderVenue/ImageUploaderVenue'

export interface IVenueFormValues {
  reimbursementPointId: number | string | null
  accessibility: IAccessibiltyFormValues
  address: string
  addressAutocomplete: string
  bannerMeta: VenueBannerMetaProps | undefined | null
  bannerUrl: string | undefined
  city: string
  comment: string
  description: string
  departmentCode: string
  email: string | null
  id: number | undefined
  isAccessibilityAppliedOnAllOffers: boolean
  isPermanent: boolean
  isVenueVirtual: boolean
  latitude: number
  longitude: number
  bookingEmail: string
  name: string
  phoneNumber: string | null
  venueSiret: number | null
  postalCode: string
  publicName: string
  siret: string
  'search-addressAutocomplete': string
  venueLabel: string | null
  venueType: string
  webSite: string | null
  withdrawalDetails: string
  isWithdrawalAppliedOnAllOffers: boolean
}
