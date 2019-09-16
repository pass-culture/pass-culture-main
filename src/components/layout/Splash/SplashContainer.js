import { connect } from 'react-redux'
import Splash from './Splash'

const mapStateToProps = ({ splash: { closeTimeout, isActive } }) => ({
  closeTimeout,
  isBetaPage: isActive,
})

export default connect(mapStateToProps)(Splash)
