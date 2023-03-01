import useActiveStep from '../useActiveStep'

jest.mock('react-router-dom-v5-compat', () => ({
  ...jest.requireActual('react-router-dom-v5-compat'),
  useLocation: () => ({
    pathname: '',
  }),
}))

describe('useActiveStep', () => {
  it('should return empty string if location is wrong', async () => {
    const activeStep = useActiveStep()
    expect(activeStep).toEqual('')
  })
})
