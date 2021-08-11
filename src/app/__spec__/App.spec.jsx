import { render, screen } from "@testing-library/react"
import React from "react"

import App from "../App"

describe("app", () => {
  it("should have website title", () => {
    // When
    render(<App />)

    // Then
    const pageTitle = screen.getByRole("heading", { level: 1 })
    expect(pageTitle).toHaveTextContent("pass Culture")
  })

  it("should have content placeholder", () => {
    // When
    render(<App />)

    // Then
    const contentPlaceHolder = screen.getByText(
      "Vous trouverez ici la liste des offres disponibles."
    )
    expect(contentPlaceHolder).toBeInTheDocument()
  })
})
