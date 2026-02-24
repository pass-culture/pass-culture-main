import { render } from '@testing-library/react'
import strokeEventsIcon from 'icons/stroke-events.svg'
import { axe } from 'vitest-axe'

import { CardInfo } from './CardInfo'

describe('<CardInfo />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <CardInfo icon={strokeEventsIcon} title="Qui réserve ?">
        Les jeunes de 15 à 21 ans réservent directement via l'application pass
        Culture.
      </CardInfo>
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
