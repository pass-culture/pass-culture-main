import useActiveStep from '../useActiveStep'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
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
