import { render, screen, within } from "@testing-library/react"
import React from "react"
import { QueryCache, QueryClient, QueryClientProvider } from "react-query"

import * as pcapi from "repository/pcapi/pcapi"
import { OfferType, ResultType, Role } from "utils/types"

import { OffersComponent as Offers } from "../Offers"

jest.mock("repository/pcapi/pcapi", () => ({
  getOffer: jest.fn(),
}))

const queryCache = new QueryCache()
const queryClient = new QueryClient({ queryCache })
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
)

const mockedPcapi = pcapi as jest.Mocked<typeof pcapi>

const searchFakeResult: ResultType = {
  objectID: "479",
  offer: {
    dates: [new Date("2021-09-29T13:54:30+00:00").valueOf()],
    name: "Une chouette à la mer",
    thumbUrl: "/storage/thumbs/mediations/AFXA",
  },
  venue: {
    name: "Le Petit Rintintin 25",
    publicName: "Le Petit Rintintin 25",
  },
}

describe("offer", () => {
  let offerInParis: OfferType
  let offerInCayenne: OfferType

  beforeEach(() => {
    queryCache.clear()
    offerInParis = {
      id: 479,
      description: "Une offre vraiment chouette",
      name: "Une chouette à la mer",
      subcategoryLabel: "Cinéma",
      stocks: [
        {
          id: 825,
          beginningDatetime: new Date("2022-09-16T00:00:00Z"),
          isBookable: true,
          price: 140000,
        },
      ],
      venue: {
        address: "1 boulevard Poissonnière",
        city: "Paris",
        name: "Le Petit Rintintin 33",
        postalCode: "75000",
        publicName: "Le Petit Rintintin 33",
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
      },
      isSoldOut: false,
      isExpired: false,
    }

    offerInCayenne = {
      id: 479,
      description: "Une offre vraiment chouette",
      name: "Une chouette à la mer",
      subcategoryLabel: "Cinéma",
      stocks: [
        {
          id: 825,
          beginningDatetime: new Date("2021-09-25T22:00:00Z"),
          isBookable: true,
          price: 80000,
        },
      ],
      venue: {
        address: "1 boulevard Poissonnière",
        city: "Paris",
        name: "Le Petit Rintintin 33",
        postalCode: "97300",
        publicName: "Le Petit Rintintin 33",
        coordinates: {
          latitude: 48.87004,
          longitude: 2.3785,
        },
      },
      isSoldOut: false,
      isExpired: false,
    }
  })

  describe("when offer has one stock", () => {
    it("should show offer informations, including one stock with the Europe/Paris timezone date when venue is located in Paris", async () => {
      // Given
      mockedPcapi.getOffer.mockResolvedValue(offerInParis)

      // When
      render(<Offers
        hits={[searchFakeResult]}
        userRole={Role.redactor}
             />, { wrapper })

      // Then
      const offerName = await screen.findByText(offerInParis.name)
      expect(offerName).toBeInTheDocument()
      const listItemsInOffer = screen.getAllByRole("listitem")
      const stockList = within(listItemsInOffer[0]).getAllByRole("listitem")
      expect(stockList).toHaveLength(1)
      const stockInformation = screen.getByText("16/09/2022 02:00, 1 400,00 €")
      expect(stockInformation).toBeInTheDocument()
    })

    it("should show offer informations, including one stock with the America/Cayenne timezone date when venue is located in Cayenne", async () => {
      // Given
      mockedPcapi.getOffer.mockResolvedValue(offerInCayenne)

      // When
      render(<Offers
        hits={[searchFakeResult]}
        userRole={Role.redactor}
             />, { wrapper })

      // Then
      const stockInformation = await screen.findByText(
        "25/09/2021 19:00, 800,00 €"
      )
      expect(stockInformation).toBeInTheDocument()
    })
  })

  describe("when offer has two stocks", () => {
    beforeEach(() => {
      offerInParis.stocks.push({
        id: 826,
        beginningDatetime: new Date("2021-10-16T00:00:00Z"),
        isBookable: true,
        price: 60000,
      })
    })

    it("should show offer informations, including two line corresponding to both stocks correctly formatted", async () => {
      // Given
      mockedPcapi.getOffer.mockResolvedValue(offerInParis)

      // When
      render(<Offers
        hits={[searchFakeResult]}
        userRole={Role.redactor}
             />, { wrapper })

      // Then
      const listItemsInOffer = await screen.findAllByRole("listitem")
      const stockList = within(listItemsInOffer[0]).getAllByRole("listitem")
      expect(stockList).toHaveLength(2)
      const firstStockInformation = screen.getByText(
        "16/09/2022 02:00, 1 400,00 €"
      )
      expect(firstStockInformation).toBeInTheDocument()
      const secondStockInformation = screen.getByText(
        "16/10/2021 02:00, 600,00 €"
      )
      expect(secondStockInformation).toBeInTheDocument()
    })

    it("should show only one stock information when the other one is not bookable", async () => {
      // Given
      offerInParis.stocks[1].isBookable = false
      mockedPcapi.getOffer.mockResolvedValue(offerInParis)

      // When
      render(<Offers
        hits={[searchFakeResult]}
        userRole={Role.redactor}
             />, { wrapper })

      // Then
      const listItemsInOffer = await screen.findAllByRole("listitem")
      const stockList = within(listItemsInOffer[0]).getAllByRole("listitem")
      expect(stockList).toHaveLength(1)
      const stockInformation = screen.getByText("16/09/2022 02:00, 1 400,00 €")
      expect(stockInformation).toBeInTheDocument()
    })
  })

  it("should show offer thumb when it exists", async () => {
    // Given
    mockedPcapi.getOffer.mockResolvedValue(offerInParis)

    // When
    render(<Offers
      hits={[searchFakeResult]}
      userRole={Role.redactor}
           />, { wrapper })

    // Then
    const offerThumb = await screen.findByRole("img")
    expect(offerThumb).toHaveAttribute(
      "src",
      expect.stringContaining(searchFakeResult.offer.thumbUrl as string)
    )
  })

  it.each`
    name                 | thumbUrl
    ${"is null"}         | ${null}
    ${"is empty string"} | ${""}
    ${"is undefined"}    | ${undefined}
  `("should show thumb placeholder when thumb $name", async ({ thumbUrl }) => {
    // Given
    mockedPcapi.getOffer.mockResolvedValue(offerInParis)
    const appSearchResult: ResultType = {
      objectID: "479",
      offer: {
        dates: [new Date("2021-09-29T13:54:30+00:00").valueOf()],
        name: "Une chouette à la mer",
        thumbUrl,
      },
      venue: {
        name: "Le Petit Rintintin 25",
        publicName: "Le Petit Rintintin 25",
      },
    }

    // When
    render(<Offers
      hits={[appSearchResult]}
      userRole={Role.redactor}
           />, { wrapper })

    // Then
    const thumbPlaceholder = await screen.findByTestId("thumb-placeholder")
    expect(thumbPlaceholder).toBeInTheDocument()
  })
})
