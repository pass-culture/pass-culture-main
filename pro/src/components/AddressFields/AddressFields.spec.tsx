import { render } from '@testing-library/react'
import type { UseFormRegisterReturn } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { AddressFields } from './AddressFields'

describe('<AddressFields />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <AddressFields
        addressRegister={
          { name: 'location' } as unknown as UseFormRegisterReturn
        }
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
