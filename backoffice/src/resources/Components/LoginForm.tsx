import React, {useState, useEffect} from 'react';
import {useLogin as userLogin} from 'react-admin';
import {Button, CardActions, CircularProgress} from '@mui/material';
import {GoogleLoginResponse, GoogleLoginResponseOffline, useGoogleLogin} from 'react-google-login'


const LoginForm = () => {


    const [loading, setLoading] = useState(false);
    const login = userLogin();

    const onLoginSucess = (response: GoogleLoginResponse | GoogleLoginResponseOffline) => {
        setLoading(false);
        if ("getAuthResponse" in response) {
            login({token: response.getAuthResponse()})
        }
    }
    const client_id = process.env.REACT_APP_OIDC_CLIENT_ID;

    const { signIn, loaded } = useGoogleLogin({
        clientId: client_id ? client_id : "",
        onSuccess: onLoginSucess,
    })


    useEffect(() => {
        const {searchParams} = new URL(window.location.href);
    }, [login])

    const handleLogin = async () => {
        setLoading(true);
        signIn();
    };

    return (
        <div>
            <CardActions>
                <Button
                    variant="contained"
                    type="submit"
                    color="primary"
                    onClick={handleLogin}
                    disabled={loading}
                >
                    {loading && (
                        <CircularProgress
                            size={18}
                            thickness={2}
                        />
                    )}
                    Login With Google
                </Button>
            </CardActions>
        </div>
    );
}

export default LoginForm;