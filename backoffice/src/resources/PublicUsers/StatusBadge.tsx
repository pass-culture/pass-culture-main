import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import {Chip} from "@mui/material";

const StatusBadge = (isActive: Boolean) => {
    let element;
    if (isActive === true) {
        element = <Chip color={"success"} label={"Actif"} icon={<CheckCircleOutlineIcon/>}/>
    } else {
        element = <Chip color={"error"} label={"Suspendu"} icon={<HighlightOffIcon/>}/>
    }
    return (
        <>
            {element}
        </>
    )
}


export default StatusBadge