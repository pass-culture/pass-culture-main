import { categoriesFactory } from "screens/OfferEducational/__tests-utils__/categoryFactory"
import { subCategoriesFactory } from "screens/OfferEducational/__tests-utils__/subCategoryFactory"

import { getEducationalCategories, getEducationalSubCategories } from "../getEducationalCategories"

const mockEducationalCategories = categoriesFactory(
  [
    {
      id: "MUSEE",
      proLabel: "Musée, patrimoine, architecture, arts visuels",
    },
    {
      id: "CINEMA",
      proLabel: "Cinéma",
    }
  ]
)

const mockEducationalSubcategories = subCategoriesFactory(
  [
    {
      id: "CINE_PLEIN_AIR",
      categoryId: "CINEMA",
      proLabel: "Cinéma plein air",
    },
    {
      id: "EVENEMENT_CINE",
      categoryId: "CINEMA",
      proLabel: "Événement cinématographique",
    },
    {
      id: "VISITE_GUIDEE",
      categoryId: "MUSEE",
      proLabel: "Visite guidée",
    }
  ]
)

const mockCategories = [...mockEducationalCategories, ...categoriesFactory(
  [
    { 
      id: "BEAUX_ARTS",
      proLabel: "Beaux-arts",
    }
  ]
)]

const mockSubcategories = [...mockEducationalSubcategories, ...subCategoriesFactory(
  [
    { 
      id: "MATERIEL_ART_CREATIF",
      categoryId: "BEAUX_ARTS",
      proLabel: "Matériel arts créatifs",
      canBeEducational: false 
    },
    {
      id: "MUSEE_VENTE_DISTANCE",
      categoryId: "MUSEE",
      proLabel: "Musée vente à distance",
      canBeEducational: false
    }
  ]
)]

describe('getEducationalCategories', () => {
  it('should return only categories having at least one subcategory that can be educational', () => {
    expect(getEducationalCategories(mockCategories, mockSubcategories)).toStrictEqual(mockEducationalCategories)
  })

  it('should return empty array when there is no subcategories', () => {
    expect(getEducationalCategories(mockCategories, [])).toStrictEqual([])
  })
})

describe('getEducationalSubCategories', () => {
  it('should return only subcategories that can be educational', () => {
    expect(getEducationalSubCategories(mockSubcategories)).toStrictEqual(mockEducationalSubcategories)
  })
})
