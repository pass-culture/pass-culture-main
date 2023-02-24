import { Route } from 'react-router-dom'

import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Activity } from 'screens/SignupJourneyForm/Activity'

const SignupJourneyRoutes = () => {
  return (
    <SignupJourneyContextProvider>
      <SignupJourneyFormLayout>
        <Route path={'/signup/authentification'}>
          <div>Authentification</div>
        </Route>
        <Route path={'/signup/activite'}>
          <Activity />
        </Route>
        <Route path={'/signup/validation'}>
          <div>Validation</div>
        </Route>
      </SignupJourneyFormLayout>
    </SignupJourneyContextProvider>
  )
}

export default SignupJourneyRoutes
