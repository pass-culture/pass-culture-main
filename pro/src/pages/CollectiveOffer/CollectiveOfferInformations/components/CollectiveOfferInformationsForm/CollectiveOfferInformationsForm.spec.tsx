import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { CollectiveOfferInformationsForm } from './CollectiveOfferInformationsForm'

describe('<CollectiveOfferInformationsForm />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<CollectiveOfferInformationsForm />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
