import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferV2 } from './IndividualOfferV2'

describe('<IndividualOfferV2 />', () => {
  it('should have no accessibility violations', async () => {
    const { container } = renderWithProviders(null, {
      initialRouterEntries: ['/offre/individuelle/v2/creation/description'],
      routes: [
        {
          path: '/offre/individuelle/v2/creation',
          element: <IndividualOfferV2 />,
          children: [{ path: 'description', element: <h2>Description</h2> }],
        },
      ],
    })

    expect(await axe(container)).toHaveNoViolations()
  })
})
