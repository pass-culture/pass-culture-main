import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'
import { categoriesFactory, subCategoriesFactory } from './categoryFactory'

import { IOfferEducationalProps } from '../OfferEducational'
import { OfferAddressType } from 'api/v1/gen'
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
    label: 'Événement cinématographique',
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
  educationalCategories: mockEducationalCategories,
  educationalSubCategories: mockEducationalSubcategories,
  getIsOffererEligible: jest.fn().mockResolvedValue({
    isOk: true,
    message: null,
    payload: { isOffererEligibleToEducationalOffer: true },
  }),
  notify: {
    success: jest.fn(),
    pending: jest.fn(),
    error: jest.fn(),
    information: jest.fn(),
  },
  mode: Mode.CREATION,
  domainsOptions: [],
  enableEducationalDomains: false,
}

const editionFormValues = {
  category: 'MUSEE',
  subCategory: 'VISITE_GUIDEE',
  title: 'offer title',
  description: 'offer description',
  duration: '',
  offererId: 'OFFERER_ID',
  venueId: 'VENUE_ID',
  eventAddress: {
    addressType: OfferAddressType.Other,
    otherAddress: 'other adress string',
    venueId: '',
  },
  participants: {
    quatrieme: true,
    troisieme: true,
    CAPAnnee1: true,
    CAPAnnee2: true,
    seconde: true,
    premiere: true,
    terminale: true,
  },
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
  notificationEmail: 'email.notification@email.com',
  domains: [],
}

export const defaultEditionProps: IOfferEducationalProps = {
  userOfferers: mockUserOfferers,
  initialValues: editionFormValues,
  onSubmit: jest.fn(),
  educationalCategories: mockEducationalCategories,
  educationalSubCategories: mockEducationalSubcategories,
  notify: {
    success: jest.fn(),
    pending: jest.fn(),
    error: jest.fn(),
    information: jest.fn(),
  },
  mode: Mode.EDITION,
  domainsOptions: [],
  enableEducationalDomains: false,
}
