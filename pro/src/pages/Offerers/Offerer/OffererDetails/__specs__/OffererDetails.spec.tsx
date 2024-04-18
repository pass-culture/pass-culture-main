import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from 'apiClient/api'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffererDetails } from '../OffererDetails'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    offererId: 'AA',
  }),
}))

describe('src | components | pages | Offerer | OffererDetails', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          name: 'fake venue',
          publicName: 'fake venue',
        },
      ],
    })
  })

  describe('render', () => {
    it('should render Venues', async () => {
      renderWithProviders(<OffererDetails />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
      expect(screen.getByText('Collaborateurs')).toBeInTheDocument()
    })

    it("shouldn't render anything if venues won't load", async () => {
      vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({
        status: HTTP_STATUS.FORBIDDEN,
      })
      renderWithProviders(<OffererDetails />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText(
          /Détails de la structure rattachée, des collaborateurs, des lieux et des fournisseurs de ses offres/
        )
      ).not.toBeInTheDocument()
    })
  })
})
