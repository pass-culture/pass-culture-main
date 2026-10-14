import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { useFocus } from '@/app/App/hook/useFocus'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { WelcomeCarousel } from './WelcomeCarousel'
import { WelcomeStepAdvantages } from './WelcomeStepAdvantages/WelcomeStepAdvantages'
import { Component as WelcomeStepCollective } from './WelcomeStepCollective/WelcomeStepCollective'
import { WelcomeStepHub } from './WelcomeStepHub/WelcomeStepHub'
import { Component as WelcomeStepIndividual } from './WelcomeStepIndividual/WelcomeStepIndividual'
import { Component as WelcomeStepNextSteps } from './WelcomeStepNextSteps/WelcomeStepNextSteps'
import { Component as WelcomeStepTarget } from './WelcomeStepTarget/WelcomeStepTarget'

const WelcomeCarouselWithFocus = () => {
  useFocus()
  return <WelcomeCarousel />
}

const renderWelcomeCarroussel = (initialPath: string = '/bienvenue') => {
  return renderWithProviders(<WelcomeCarousel />, {
    initialRouterEntries: [initialPath],
  })
}
describe('<WelcomeCarousel />', () => {
  it('should focus the step heading after navigating forwards and backwards', async () => {
    renderWithProviders(<WelcomeCarouselWithFocus />, {
      initialRouterEntries: ['/bienvenue'],
      routes: [
        {
          path: '/bienvenue',
          element: <WelcomeCarouselWithFocus />,
          children: [
            { index: true, element: <WelcomeStepHub /> },
            { path: 'publics', element: <WelcomeStepTarget /> },
            { path: 'offres-jeunes', element: <WelcomeStepIndividual /> },
            { path: 'offres-scolaires', element: <WelcomeStepCollective /> },
            { path: 'avantages', element: <WelcomeStepAdvantages /> },
            { path: 'prochaines-etapes', element: <WelcomeStepNextSteps /> },
          ],
        },
      ],
    })

    expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()
    await userEvent.click(
      screen.getByRole('radio', { name: /Partenaire culturel/ })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()

    await userEvent.click(screen.getByRole('link', { name: 'Précédent' }))
    expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()

    await userEvent.click(
      screen.getByRole('radio', { name: /Partenaire culturel/ })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    for (let step = 0; step < 4; step++) {
      await userEvent.click(screen.getByRole('link', { name: 'Suivant' }))
      expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()
    }
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderWelcomeCarroussel()

    expect(await axe(container)).toHaveNoViolations()
  })
})
