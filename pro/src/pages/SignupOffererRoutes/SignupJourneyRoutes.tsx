import { Routes, Route } from 'react-router-dom-v5-compat'

import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { Activity } from 'screens/SignupJourneyForm/Activity'

const SignupJourneyRoutes = () => {
  return (
    <SignupJourneyFormLayout>
      <Routes>
        <Route path={'/authentification'}>
          <div>Authentification</div>
        </Route>
        <Route path={'/activite'}>
          <Activity />
        </Route>
        <Route path={'/signup/validation'}>
          <div>Validation</div>
        </Route>
      </Routes>
    </SignupJourneyFormLayout>
  )
}

export default SignupJourneyRoutes
