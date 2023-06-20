import { Mode } from 'core/OfferEducational'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { OfferEducationalProps } from '../OfferEducational'

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

export const defaultCreationProps: OfferEducationalProps = {
  userOfferers: mockUserOfferers,
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
  isTemplate: false,
  setOffer: jest.fn(),
}

export const defaultEditionProps: OfferEducationalProps = {
  offer: collectiveOfferFactory(),
  userOfferers: mockUserOfferers,
  categories: {
    educationalCategories: mockEducationalCategories,
    educationalSubCategories: mockEducationalSubcategories,
  },
  mode: Mode.EDITION,
  domainsOptions: [{ value: 1, label: 'domain1' }],
  isTemplate: false,
  setOffer: jest.fn(),
}
