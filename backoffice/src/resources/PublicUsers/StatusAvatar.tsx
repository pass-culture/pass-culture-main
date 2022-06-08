import {green, red, yellow} from "@mui/material/colors";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import {Avatar} from "@mui/material";
import React from "react";

export default function StatusAvatar(subscriptionItem: string) {
    let color, icon;

    switch (subscriptionItem) {
        case 'ok':
            color = green["700"]
            icon = <CheckCircleOutlineIcon/>
            break;
        case 'ko':
            color = red["700"]
            icon = <ErrorOutlineIcon/>
            break;
        default:
            color = yellow["700"]
            icon = <ErrorOutlineIcon/>
    }

    return (
        <Avatar sx={{bgcolor: color}}>{icon}</Avatar>
    )
}