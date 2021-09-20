import { SearchProvider } from "@elastic/react-search-ui"
import { render, screen } from "@testing-library/react"
import React from "react"

import * as pcapi from "repository/pcapi/pcapi"
import { Role, VenueFilterType } from "utils/types"

import { App } from "../App"

jest.mock("utils/config", () => ({
  APP_SEARCH_ENDPOINT: "app-search-endpoint",
  APP_SEARCH_KEY: "app-search-key",
}))

jest.mock("@elastic/react-search-ui", () => {
  return {
    ...jest.requireActual("@elastic/react-search-ui"),
    SearchProvider: jest.fn(({ children }) => children),
    WithSearch: jest.fn(({ children }) => children({ results: [] })),
    SearchBox: jest.fn().mockReturnValue(null),
  }
})

jest.mock("repository/pcapi/pcapi", () => ({
  authenticate: jest.fn(),
  getVenueBySiret: jest.fn(),
}))
const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

describe("app", () => {
  describe("when is authenticated", () => {
    let venue: VenueFilterType

    beforeEach(() => {
      Reflect.deleteProperty(global.window, "location")
      window.location = new URL("https://www.example.com")

      venue = {
        id: 1436,
        name: "Librairie de Paris",
        publicName: "Librairie de Paris",
      }

      mockedPcapi.authenticate.mockResolvedValue(Role.redactor)
      mockedPcapi.getVenueBySiret.mockResolvedValue(venue)
    })

    afterEach(() => {
      SearchProvider.mockClear()
    })

    it("should show search offers input with no filter on venue when no siret is provided", async () => {
      // When
      render(<App />)

      // Then
      const contentTitle = await screen.findByText("Rechercher une offre", {
        selector: "h2",
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = SearchProvider.mock.calls[0][0]
      expect(searchConfiguration.config.searchQuery.filters).toStrictEqual([
        { field: "is_educational", values: [1] },
      ])
      expect(screen.queryByText("Lieu filtré :")).not.toBeInTheDocument()
      expect(mockedPcapi.getVenueBySiret).not.toHaveBeenCalled()
    })

    it("should show search offers input with filter on venue when siret is provided", async () => {
      // Given
      const siret = "123456789"
      Reflect.deleteProperty(global.window, "location")
      window.location = new URL(`https://www.example.com?siret=${siret}`)

      // When
      render(<App />)

      // Then
      const contentTitle = await screen.findByText("Rechercher une offre", {
        selector: "h2",
      })
      expect(contentTitle).toBeInTheDocument()
      const searchConfiguration = SearchProvider.mock.calls[0][0]
      expect(searchConfiguration.config.searchQuery.filters).toStrictEqual([
        { field: "is_educational", values: [1] },
        { field: "venue_id", values: [venue.id] },
      ])
      expect(screen.getByText("Lieu filtré :")).toBeInTheDocument()
      expect(screen.getByText(venue.name)).toBeInTheDocument()
      expect(mockedPcapi.getVenueBySiret).toHaveBeenCalledWith(siret)
    })
  })

  describe("when is not authenticated", () => {
    beforeEach(() => {
      mockedPcapi.authenticate.mockRejectedValue("Authentication failed")
    })

    it("should show error page", async () => {
      // When
      render(<App />)

      // Then
      const contentTitle = await screen.findByText(
        "Une erreur s’est produite.",
        { selector: "h1" }
      )
      expect(contentTitle).toBeInTheDocument()
      expect(screen.queryByRole("textbox")).not.toBeInTheDocument()
    })
  })
})
