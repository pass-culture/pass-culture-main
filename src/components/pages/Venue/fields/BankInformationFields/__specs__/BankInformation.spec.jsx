import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import BankInformation from '../BankInformationFields'

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

const renderBankInformation = async props => {
  return await act(async () => {
    await render(<BankInformation {...props} />)
  })
}

describe('src | Venue | BankInformation', () => {
  const venue = {
    id: 'AA',
    name: 'fake venue name',
  }
  const offerer = {
    id: 'BB',
    name: 'fake offerer name',
  }

  let props
  beforeEach(() => {
    props = { venue, offerer }
  })

  describe('when no application has been made or application has been refused', () => {
    describe('when the offerer has no bank information', () => {
      it('should render instruction block', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
          },
        }

        // when
        await renderBankInformation(props)

        // then
        expect(screen.getByText('Coordonnées bancaires du lieu')).toBeInTheDocument()
        expect(
          screen.getByText(
            'Renseignez vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles'
          )
        ).toBeInTheDocument()

        const createDataLink = screen.getByText('Renseignez les coordonnées bancaires du lieu')
        expect(createDataLink).toBeInTheDocument()
        expect(createDataLink).toHaveAttribute(
          'href',
          'link/to/venue/demarchesSimplifiees/procedure'
        )

        const informationLink = screen.getByText('En savoir plus sur les remboursements')
        expect(informationLink).toBeInTheDocument()
        expect(informationLink).toHaveAttribute(
          'href',
          'https://aide.passculture.app/fr/article/acteurs-determiner-ses-modalites-de-remboursement-1ab6g2m/'
        )
      })
    })

    describe('when the offerer has bank information', () => {
      it('should render offerer information', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
          },
          offerer: {
            ...offerer,
            bic: 'offererBic',
            iban: 'offererIban',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        expect(screen.getByText(props.offerer.bic)).toBeInTheDocument()
        expect(screen.getByText(props.offerer.iban)).toBeInTheDocument()
      })
    })
  })

  describe('when application has been validated', () => {
    describe('when venue and offerer banking information are both provided', () => {
      it('should render venue informations', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: 'venueBic',
            iban: 'venueIban',
          },
          offerer: {
            ...offerer,
            bic: 'offererBic',
            iban: 'offererIban',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        expect(screen.getByText(props.venue.bic)).toBeInTheDocument()
        expect(screen.getByText(props.venue.iban)).toBeInTheDocument()
      })
    })
  })

  describe('when application is in construction or in instruction', () => {
    describe('when offerer has no bank informations', () => {
      it('should render current application detail', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
            demarchesSimplifieesApplicationId: '12',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        const expectedUrl = `https://www.demarches-simplifiees.fr/dossiers/${props.venue.demarchesSimplifieesApplicationId}`
        const seeDataLink = screen.getByText('Accéder au dossier')
        expect(seeDataLink).toBeInTheDocument()
        expect(seeDataLink).toHaveAttribute('href', expectedUrl)
      })
    })

    describe('when offerer has bank informations', () => {
      it('should render current application detail and offerer bank informations', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
            demarchesSimplifieesApplicationId: '12',
          },
          offerer: {
            ...offerer,
            bic: 'offererBic',
            iban: 'offererIban',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        const expectedUrl = `https://www.demarches-simplifiees.fr/dossiers/${props.venue.demarchesSimplifieesApplicationId}`
        const seeDataLink = screen.getByText('Accéder au dossier')
        expect(seeDataLink).toBeInTheDocument()
        expect(seeDataLink).toHaveAttribute('href', expectedUrl)

        expect(screen.getByText(props.offerer.bic)).toBeInTheDocument()
        expect(screen.getByText(props.offerer.iban)).toBeInTheDocument()
      })

      it('should render current application detail when demarchesSimplifieesApplicationId is provided', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
            demarchesSimplifieesApplicationId: '12',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        const expectedUrl = `https://www.demarches-simplifiees.fr/dossiers/${props.venue.demarchesSimplifieesApplicationId}`
        const seeDataLink = screen.getByText('Accéder au dossier')
        expect(seeDataLink).toBeInTheDocument()
        expect(seeDataLink).toHaveAttribute('href', expectedUrl)

        expect(await screen.queryByText('BIC')).not.toBeInTheDocument()
        expect(await screen.queryByText('IBAN')).not.toBeInTheDocument()
      })

      it('should render current application detail and offerer bank informations when both presents in props', async () => {
        // Given
        props = {
          ...props,
          venue: {
            ...venue,
            bic: null,
            iban: null,
            demarchesSimplifieesApplicationId: '12',
          },
          offerer: {
            ...offerer,
            bic: 'offererBic',
            iban: 'offererIban',
          },
        }

        // when
        await renderBankInformation(props)

        // then
        const expectedUrl = `https://www.demarches-simplifiees.fr/dossiers/${props.venue.demarchesSimplifieesApplicationId}`
        const seeDataLink = screen.getByText('Accéder au dossier')
        expect(seeDataLink).toBeInTheDocument()
        expect(seeDataLink).toHaveAttribute('href', expectedUrl)

        expect(screen.getByText(props.offerer.bic)).toBeInTheDocument()
        expect(screen.getByText(props.offerer.iban)).toBeInTheDocument()
      })
    })
  })
})
