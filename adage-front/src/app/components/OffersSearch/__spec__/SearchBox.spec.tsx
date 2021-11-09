import {
  createEvent,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react"
import React from "react"

import { SearchBoxComponent as SearchBox } from "../SearchBox"

const placeholder =
  "Nom de l'offre, du lieu ou de la catégorie (films, visites, conférences, spectacles, cours, musique)"

describe("searchBox", () => {
  it("should have correct placeholder", () => {
    // Given
    const refine = jest.fn()

    // When
    render(<SearchBox
      currentRefinement=""
      refine={refine}
           />)

    // Then
    expect(screen.getByPlaceholderText(placeholder)).toBeInTheDocument()
  })

  it("should call refine on text change", () => {
    // Given
    const refine = jest.fn()

    // When
    render(<SearchBox
      currentRefinement=""
      refine={refine}
           />)
    const textInput = screen.getByPlaceholderText(placeholder)
    fireEvent.change(textInput, { target: { value: "a" } })

    // Then
    expect(refine).toHaveBeenNthCalledWith(1, "a")
  })

  it("should not refresh on submit", () => {
    // Given
    const refine = jest.fn()

    // When
    const { getByText } = render(
      <SearchBox
        currentRefinement="jeu"
        refine={refine}
      />
    )
    const clickEvent = createEvent.click(getByText("Rechercher"))
    fireEvent(getByText("Rechercher"), clickEvent)

    // Then
    waitFor(() => {
      expect(clickEvent.defaultPrevented).toBeTruthy()
    })
  })
})
