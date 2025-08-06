import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { createRef } from 'react'

import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultVenueProvider } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueProviderCard, VenueProviderCardProps } from '../VenueProviderCard'

const renderVenueProviderCard = async (props: VenueProviderCardProps) => {
  renderWithProviders(<VenueProviderCard {...props} />)

  await waitFor(() => screen.getByText('Supprimer'))
}

describe('VenueProviderCard', () => {
  let props: VenueProviderCardProps
  const offererId = 3

  beforeEach(() => {
    props = {
      offererId: offererId,
      venue: defaultGetVenue,
      venueProvider: defaultVenueProvider,
      selectSoftwareButtonRef: createRef(),
    }
  })

  describe('integration provider with on going sync', () => {
    beforeEach(() => {
      props.venueProvider.isActive = true
    })

    it('should display cinema provider info', async () => {
      await renderVenueProviderCard(props)

      const providerNameDiv = screen.getByText('Ciné Office')
      const providerLogo = screen.getByRole('img', { name: 'Ciné Office' })

      expect(providerNameDiv).toBeInTheDocument()
      expect(providerLogo).toBeInTheDocument()
    })

    it('should display edit button', async () => {
      await renderVenueProviderCard(props)

      const cinemaProviderEditButton = screen.getByRole('button', {
        name: 'Paramétrer',
      })
      expect(cinemaProviderEditButton).toBeInTheDocument()

      await userEvent.click(cinemaProviderEditButton)

      expect(
        screen.getByText('Modifier les paramètres de vos offres')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Accepter les réservations “Duo“')
      ).toBeInTheDocument()
    })

    it('should display delete and pause buttons', async () => {
      await renderVenueProviderCard(props)

      const cinemaProviderDeleteButton = screen.getByRole('button', {
        name: 'Supprimer',
      })
      const cinemaProviderPauseButton = screen.getByRole('button', {
        name: 'Mettre en pause la synchronisation Mettre en pause',
      })
      expect(cinemaProviderDeleteButton).toBeInTheDocument()
      expect(cinemaProviderPauseButton).toBeInTheDocument()
    })

    it('should display on going sync info', async () => {
      await renderVenueProviderCard(props)

      const onGoingSyncDiv = screen.getByText(
        'Importation en cours. Cette étape peut durer plusieurs dizaines de minutes.'
      )
      const account = screen.getByText('Compte :')
      const venueIdAtOfferProviderInfo = screen.getByText(
        `${props.venueProvider.venueIdAtOfferProvider}`
      )
      expect(onGoingSyncDiv).toBeInTheDocument()
      expect(account).toBeInTheDocument()
      expect(venueIdAtOfferProviderInfo).toBeInTheDocument()
    })
  })

  describe('synched integration provider', () => {
    beforeEach(() => {
      props.venueProvider.lastSyncDate = '2021-08-16T00:00:00Z'
    })

    it('should display sync info', async () => {
      await renderVenueProviderCard(props)

      const syncDiv = screen.getByText('Dernière synchronisation :')
      const lastSyncDate = screen.getByText('16/08/2021 à 02:00')
      const account = screen.getByText('Compte :')
      const venueIdAtOfferProviderInfo = screen.getByText(
        `${props.venueProvider.venueIdAtOfferProvider}`
      )
      expect(syncDiv).toBeInTheDocument()
      expect(lastSyncDate).toBeInTheDocument()
      expect(account).toBeInTheDocument()
      expect(venueIdAtOfferProviderInfo).toBeInTheDocument()
    })
  })

  describe('Allociné provider', () => {
    beforeEach(() => {
      props.venueProvider.provider.name = 'Allociné'
    })

    it('should display allociné spécific info', async () => {
      await renderVenueProviderCard(props)

      const providerNameDiv = screen.getByText('Allociné')
      const providerLogo = screen.getByRole('img', { name: 'Allociné' })

      expect(providerNameDiv).toBeInTheDocument()
      expect(providerLogo).toBeInTheDocument()
    })
  })

  describe('public API provider', () => {
    beforeEach(() => {
      props.venueProvider.provider.hasOffererProvider = true
    })

    it('should display creation date info', async () => {
      await renderVenueProviderCard(props)

      const creationDate = screen.getByText('15/08/2021 à 02:00')
      const creationDateText = screen.getByText("Date d'ajout :")

      expect(creationDate).toBeInTheDocument()
      expect(creationDateText).toBeInTheDocument()
    })
  })
})
