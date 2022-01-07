import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'

import { IOfferEducationalProps } from '../OfferEducational'

import { categoriesFactory } from './categoryFactory'
import { subCategoriesFactory } from './subCategoryFactory'
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
}
