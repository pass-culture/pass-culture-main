import {
    Card,
    CardContent,
    CardHeader,
    Grid,
    Typography,
    List,
    CardActions,
    Box,
    Button, Chip
} from "@mui/material";
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import {
    Form,
    ReferenceField,
    SearchInput,
    ShowButton, TextField,
    Title,
    useAuthenticated,
    useRedirect
} from "react-admin";
import {dataProvider} from "../../providers/dataProvider";
import {ClassAttributes, HTMLAttributes, useState} from "react";
import SearchIcon from '@mui/icons-material/Search';

const UpperCaseText = (props: JSX.IntrinsicAttributes & ClassAttributes<HTMLSpanElement> & HTMLAttributes<HTMLSpanElement>) => (
    <span {...props} style={{
        textTransform: "uppercase",
    }}>
    </span>
)


const UserCard = (props: { record: any; }) => {
    const record = props.record;
    let statusBadge, activeBadge;
    switch (record['roles'][0]) {
        case "BENEFICIARY":
            statusBadge = <Chip color={"secondary"} label={'Pass 18'}/>
            break;
        case "UNDERAGE_BENEFICIARY":
            statusBadge = <Chip color={"secondary"} label={'Pass 15-17'}/>
            break;
        default:
            break;
    }

    switch (record["isActive"]) {
        case true:
            activeBadge = <Chip icon={<CheckCircleOutlineIcon/>} color={"success"} label={'Actif'}/>
            break;
        case false:
            activeBadge = <Chip icon={<HighlightOffIcon/>} color={"error"} label={'Suspendu'}/>
            break;
        default:
            break;
    }

    return (
        <Card sx={{minWidth: 275}}>
            <CardContent>
                <div>
                    {activeBadge} &nbsp;&nbsp;
                    {statusBadge}
                </div>
                <br/>
                <Typography
                    variant="subtitle1"
                    component="h4"
                    align="left"
                >
                    {record["firstName"]} <UpperCaseText>{record["lastName"]}</UpperCaseText>
                </Typography>
                <Typography
                    variant="subtitle2"
                    component="h5"
                    align="left"
                >
                    <ReferenceField source="id" reference="/public_accounts/users/">
                        <Typography >
                            id user : {record["id"]}
                        </Typography>
                    </ReferenceField>
                </Typography>
                <Typography
                    variant="body1"
                    component="p"
                    align="left"
                >
                    <b>e-mail</b>: {record["email"]}
                </Typography>
                <Typography
                    variant="body1"
                    component="p"
                    align="left"
                >
                    <b>tél : </b> {record["phoneNumber"]}
                </Typography>

            </CardContent>
            <CardActions>
                <ShowButton resource={'public_accounts/user'} label={"Consulter ce profil"}/>

                <Button href={`/public_accounts/user/${record.id}`} variant={"text"} color={"secondary"} >Consulter ce profil</Button>
            </CardActions>
        </Card>
    )
}


const UserSearch = () => {
    const [userData, setUserData] = useState([])
    // useAuthenticated();
    return <Grid
        container
        spacing={0}
        direction="column"
        alignItems="center"
        justifyContent="center"
    >
        <Card
            style={{
                boxShadow: "none",
                width: "100%",
                paddingTop: "20px"
            }}
        >
            {/*<CardHeader
                title={'Jeunes et grand public'}
                component={"h1"}
            />*/}
            <CardContent>
                <Typography variant="h2" component="div"
                            textAlign={(userData.length === 0) ? "center" : "left"} >
                    &nbsp;
                </Typography>

                <Typography variant={"subtitle1"} component={"p"} mb={2} gutterBottom
                            textAlign={(userData.length === 0) ? "center" : "left"}>
                    Recherche un utilisateur à partir de son nom, mail ou numéro de téléphone
                </Typography>
                <Grid container justifyContent={(userData.length === 0) ? "center" : "left"}>


                    <Box>
                        <Form

                            onSubmit={(params) => {
                                if (params && params.search) {
                                    setUserData([])

                                    dataProvider.searchList('public_accounts/search', String(params.search), {
                                        // @ts-ignore
                                        token: JSON.parse(localStorage.getItem('token')).id_token
                                    }).then((response: any) => {
                                        if (response && response.data && response.data.length > 0) {
                                            setUserData(response.data)
                                        }

                                    })
                                }
                            }}>
                            <div style={{
                                justifyContent: "center",
                                textAlign: "center"
                            }}>
                                <SearchInput
                                    helperText={false}
                                    source={"q"} name={"search"}
                                    type={"text"}
                                    fullWidth={(userData.length === 0)}
                                    variant={"filled"}
                                    style={{
                                        marginLeft: "auto",
                                        marginRight: 5,

                                    }}
                                    onKeyUp={event => {
                                        if (event.key === 'Enter') {
                                            event.stopPropagation();
                                        }
                                    }}
                                />

                                <Button type={"submit"} variant="contained" size={"small"} endIcon={<SearchIcon/>}>
                                    Chercher
                                </Button>
                            </div>
                        </Form>
                    </Box>

                </Grid>
                {userData.length > 0 && (<div>{userData.length} résultat(s)</div>)}

            </CardContent>
        </Card>
        <List>

            <Grid container spacing={2} sx={{marginTop: '1em', minWidth: 275}}>
                {userData.map(record => (
                    <Grid key={record["id"]} sx={{minWidth: 275}} xs={12} sm={6} md={4} lg={4} xl={4} item>
                        <UserCard record={record}/>
                    </Grid>
                ))}
            </Grid>
        </List>
    </Grid>
};

export default UserSearch;