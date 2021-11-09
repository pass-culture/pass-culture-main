import { categoriesFactory } from "../../../../__tests-utils__/categoryFactory"
import { subCategoriesFactory } from "../../../../__tests-utils__/subCategoryFactory"
import { buildOptions } from "../buildOptions"

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

describe('buildOptions', () => {
  it('should build options for categories', () => {
    expect(buildOptions(mockEducationalCategories)).toStrictEqual([
      { value: 'MUSEE', label: 'Musée, patrimoine, architecture, arts visuels' },
      { value: 'CINEMA', label: 'Cinéma' }
    ])
  })

  it('should build options for subcategories', () => {
    expect(buildOptions(mockEducationalSubcategories)).toStrictEqual([
      { value: 'CINE_PLEIN_AIR', label: 'Cinéma plein air' },
      { value: 'EVENEMENT_CINE', label: 'Événement cinématographique' },
      { value: 'VISITE_GUIDEE', label: 'Visite guidée' },
    ])
  })
})
