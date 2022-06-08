import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import {Chip} from "@mui/material";
import {PublicUserRolesEnum} from "../Interfaces/UserSearchInterface";

const BeneficiaryBadge = (role: PublicUserRolesEnum) => {
    let element;
  switch (role) {
      case PublicUserRolesEnum.beneficiary:
          element = <Chip color={"secondary"} label={'Pass 18'}/>
          break;
      case PublicUserRolesEnum.underageBeneficiary:
          element = <Chip color={"secondary"} label={'Pass 15-17'}/>
          break;
      default:
          break;
  }
    return (
        <>
            {element}
        </>
    )
}


export default BeneficiaryBadge