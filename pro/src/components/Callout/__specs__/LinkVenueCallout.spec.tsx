import { screen } from '@testing-library/react'
import React from 'react'

import LinkVenueCallout, {
  LinkVenueCalloutProps,
} from 'components/Callout/LinkVenueCallout'
import { renderWithProviders } from 'utils/renderWithProviders'

describe('LinkVenueCallout', () => {
  let props: LinkVenueCalloutProps = {
    titleOnly: false,
  }
  it('should not render LinkVenueCallout without FF', () => {
    renderWithProviders(<LinkVenueCallout {...props} />)

    expect(
      screen.queryByText(/Dernière étape pour vous faire rembourser/)
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        /Afin de percevoir vos remboursements, vous devez rattacher vos lieux/
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Gérer le rattachement de mes lieux',
      })
    ).not.toBeInTheDocument()
  })

  describe('With FF enabled', () => {
    const storeOverrides = {
      features: {
        list: [
          { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      },
    }

    it('should render LinkVenueCallout', () => {
      renderWithProviders(<LinkVenueCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.getByText(/Dernière étape pour vous faire rembourser/)
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Afin de percevoir vos remboursements, vous devez rattacher/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Gérer le rattachement de mes lieux',
        })
      ).toBeInTheDocument()
    })

    it('should render LinkVenueCallout with singular wording', () => {
      props.titleOnly = false
      renderWithProviders(<LinkVenueCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.getByText(
          /Dernière étape pour vous faire rembourser : rattachez votre lieu/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Afin de percevoir vos remboursements, vous devez rattacher votre lieu/
        )
      ).toBeInTheDocument()
    })

    it('should render LinkVenueCallout with singular plural', () => {
      props = {
        titleOnly: false,
        hasMultipleVenuesToLink: true,
      }
      renderWithProviders(<LinkVenueCallout {...props} />, {
        storeOverrides,
      })

      expect(
        screen.getByText(
          /Dernière étape pour vous faire rembourser : rattachez vos lieux/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Afin de percevoir vos remboursements, vous devez rattacher vos lieux/
        )
      ).toBeInTheDocument()
    })
  })
})
