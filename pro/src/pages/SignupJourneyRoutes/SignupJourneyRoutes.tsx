import { Route, Routes } from 'react-router-dom-v5-compat'

import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout'
import { SignupJourneyContextProvider } from 'context/SignupJourneyContext'
import { Activity } from 'screens/SignupJourneyForm/Activity'

const SignupJourneyRoutes = () => {
  return (
    <SignupJourneyContextProvider>
      <SignupJourneyFormLayout>
        <Routes>
          <Route path={'/authentification'} element={<>Authentification</>} />
          <Route path={'/activite'} element={<Activity />} />
          <Route path={'/validation'} element={<>Validation</>} />
        </Routes>
      </SignupJourneyFormLayout>
    </SignupJourneyContextProvider>
  )
}

export default SignupJourneyRoutes
