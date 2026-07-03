import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdditionalFeeTypeInput } from './AdditionalFeeTypeInput'

describe('AdditionalFeeTypeInput – onBlur', () => {
  it('should reset the input to empty when user typed something without confirming', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()

    renderWithProviders(
      <AdditionalFeeTypeInput
        collectiveAdditionalFee={{
          type: CollectiveAdditionalFeeType.OTHER,
          label: '',
          amount: 0,
        }}
        name="type"
        disabled={false}
        onChange={handleChange}
      />
    )

    const input = screen.getByLabelText(/Type de frais annexes/)

    await user.type(input, 'frais divers')
    expect(input).toHaveValue('frais divers')

    await user.tab()

    expect(screen.getByLabelText(/Type de frais annexes/)).toHaveValue('')
    expect(handleChange).toHaveBeenLastCalledWith({
      type: CollectiveAdditionalFeeType.OTHER,
      label: '',
    })
  })

  it('should sync form with reset value when user typed and blurred without confirming', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()

    renderWithProviders(
      <AdditionalFeeTypeInput
        collectiveAdditionalFee={{
          type: CollectiveAdditionalFeeType.OTHER,
          label: 'valeur confirmée',
          amount: 0,
        }}
        name="type"
        disabled={false}
        onChange={handleChange}
      />
    )

    await user.type(screen.getByLabelText(/Type de frais annexes/), 'new value')
    await user.tab()

    expect(handleChange).toHaveBeenLastCalledWith({
      type: CollectiveAdditionalFeeType.OTHER,
      label: 'valeur confirmée',
    })
  })
})
