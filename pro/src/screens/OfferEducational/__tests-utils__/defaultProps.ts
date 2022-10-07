import { OfferAddressType, SubcategoryIdEnum } from 'apiClient/v1'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
} from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

import { IOfferEducationalProps } from '../OfferEducational'

import { categoriesFactory, subCategoriesFactory } from './categoryFactory'
import { userOfferersFactory } from './userOfferersFactory'

const mockEducationalCategories = categoriesFactory([
  {
    id: 'MUSEE',
    label: 'Musée, patrimoine, architecture, arts visuels',
  },
  {
    id: 'CINEMA',
    label: 'Cinéma',
  },
])

const mockEducationalSubcategories = subCategoriesFactory([
  {
    id: 'CINE_PLEIN_AIR',
    categoryId: 'CINEMA',
    label: 'Cinéma plein air',
  },
  {
    id: 'EVENEMENT_CINE',
    categoryId: 'CINEMA',
    label: 'Évènement cinématographique',
  },
  {
    id: 'VISITE_GUIDEE',
    categoryId: 'MUSEE',
    label: 'Visite guidée',
  },
])

const mockUserOfferers = userOfferersFactory([{}])

export const defaultCreationProps: IOfferEducationalProps = {
  userOfferers: mockUserOfferers,
  initialValues: DEFAULT_EAC_FORM_VALUES,
  onSubmit: jest.fn(),
  categories: {
    educationalCategories: mockEducationalCategories,
    educationalSubCategories: mockEducationalSubcategories,
  },
  getIsOffererEligible: jest.fn().mockResolvedValue({
    isOk: true,
    message: null,
    payload: { isOffererEligibleToEducationalOffer: true },
  }),
  mode: Mode.CREATION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
}

const allParticipantsOptionsToTrue = {
  all: false,
  ...buildStudentLevelsMapWithDefaultValue(true),
}

const editionFormValues: IOfferEducationalFormValues = {
  category: 'MUSEE',
  subCategory: SubcategoryIdEnum.VISITE_GUIDEE,
  title: 'offer title',
  description: 'offer description',
  duration: '',
  offererId: 'OFFERER_ID',
  venueId: 'VENUE_ID',
  eventAddress: {
    addressType: OfferAddressType.OTHER,
    otherAddress: 'other adress string',
    venueId: '',
  },
  interventionArea: [],
  participants: allParticipantsOptionsToTrue,
  accessibility: {
    visual: true,
    audio: true,
    motor: true,
    mental: true,
    none: false,
  },
  phone: '0466841425',
  email: 'email@email.com',
  notifications: true,
  notificationEmails: ['email.notification@email.com'],
  domains: [],
  'search-domains': '',
  'search-interventionArea': '',
}

export const defaultEditionProps: IOfferEducationalProps = {
  userOfferers: mockUserOfferers,
  initialValues: editionFormValues,
  onSubmit: jest.fn(),
  categories: {
    educationalCategories: mockEducationalCategories,
    educationalSubCategories: mockEducationalSubcategories,
  },
  mode: Mode.EDITION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
}
