import useActiveStep from '../useActiveStep'

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
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
