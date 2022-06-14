import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import {Chip} from "@mui/material";

const StatusBadge = (isActive: Boolean) => {
    if (isActive === true) {
        return <Chip color={"success"} label={"Actif"} icon={<CheckCircleOutlineIcon/>}/>
    }
    return <Chip color={"error"} label={"Suspendu"} icon={<HighlightOffIcon/>}/>
}

export default StatusBadge
