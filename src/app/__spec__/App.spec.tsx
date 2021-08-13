import { render, screen } from "@testing-library/react"
import React from "react"

import * as pcapi from "repository/pcapi/pcapi"

import App from "../App"

jest.mock("repository/pcapi/pcapi", () => ({
  authenticate: jest.fn(),
}))

describe("app", () => {
  describe("when is authenticated", () => {
    beforeEach(() => {
      pcapi.authenticate.mockResolvedValue()
    })

    it("should have content placeholder", async () => {
      // When
      render(<App />)

      // Then
      const pageTitle = screen.getByRole("heading", { level: 1 })
      expect(pageTitle).toHaveTextContent("pass Culture")
      const contentTitle = await screen.findByText("Bienvenue", {
        selector: "h2",
      })
      expect(contentTitle).toBeInTheDocument()
      const contentPlaceHolder = screen.getByText(
        "Vous trouverez ici la liste des offres disponibles."
      )
      expect(contentPlaceHolder).toBeInTheDocument()
    })
  })

  describe("when is not authenticated", () => {
    beforeEach(() => {
      pcapi.authenticate.mockRejectedValue()
    })

    it("should tell user that he is not authorized to access this page", async () => {
      // When
      render(<App />)

      // Then
      const pageTitle = screen.getByRole("heading", { level: 1 })
      expect(pageTitle).toHaveTextContent("pass Culture")
      const contentTitle = await screen.findByText(
        "Vous n'êtes pas autorisé à accéder à cette page",
        { selector: "h2" }
      )
      expect(contentTitle).toBeInTheDocument()
    })
  })
})
