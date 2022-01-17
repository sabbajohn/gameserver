window.auth_data = null;
window.purchase_object = [];

window.fbAsyncInit = function () {
    // console.log("ON window.fbAsyncInit");
    // initialize facebook sdk
    FB.init({
        appId: '354159478852902',
        autoLogAppEvents: true,
        xfbml: true,
        version: 'v8.0'
    });

    // what happens when we log in :)
    window.onlogin = function (response) {
        let grab_site_params = new URL(window.location.href).searchParams;
        let site_id = grab_site_params.get("q")
        let facebook_games = JSON.parse(grab_site_params.get("f"))
        // console.log("ON window.onlogin");
        var uid = response.authResponse.userID;
        var accessToken = response.authResponse.accessToken;
        FB.api('/me?fields=id,name,picture.type(large),email', function (response) {
            console.log('Good to see you, ' + response.name + '.');
            // console.log(JSON.stringify(response));
            window.auth_data = {
                "uid": uid,
                "token": accessToken,
                "userinfo": response,
                site_id,
                facebook_games
            };
            // console.log(JSON.stringify(window.auth_data));
        });
        // get all in app available products
        FB.api("354159478852902/products", function (response) {
            if (response && !response.error) {
                window.purchase_object = response
                // console.log(window.purchase_object)
            }
        });
    };

    window.purchaseiap_q = []; // queue for requests being processed
    window.purchaseiap_r = []; // queue for finished requests

    window.logout = function () {
        console.log("ON window.logout");
        FB.logout(function (response) {
            console.log("Good bye")
            // console.log(JSON.stringify(response));
        });
    }

    window.onpurchaseiap = function (response) {
        // console.log("ON window.onpurchaseiap");
        // console.log(response);
        if (!response) {
            // console.log('Error on onpurchaseiap = User closed purchase window');
            return
        }
        if ('error_code' in response) {
            console.log('Error on onpurchaseiap = ' + JSON.stringify(response));
            return
        }
        window.purchaseiap_q = window.purchaseiap_q.filter(
            o => o['developer_payload'] != response['developer_payload']
        );
        window.purchaseiap_r.push(response);

        // TEMP HACK, check https://stackoverflow.com/questions/45400242/payments-lite-serverless-first-purchase-works-but-the-second-always-fails -->
        // we are going to do this server-side using the graph api, as in that link :)
        FB.api('/' + response['purchase_token'] + '/consume',
            'post', {
                access_token: window.auth_data['token']
            },
            result => {
                console.log('consuming product', response['product_id'], 'with purchase token', response['purchase_token']);
                // console.log(JSON.stringify(result));
            }
        );
    }

    window.dopurchaseiap = function (item_id, request_id) {
        // console.log("ON window.dopurchaseiap");

        if (!item_id)
            item_id = 'fichas100000';

        if (!request_id)
            request_id = Math.floor(Math.random() * 10000000000).toString();

        obj = {
            method: 'pay',
            action: 'purchaseiap',
            product_id: item_id,
            developer_payload: request_id
        };

        window.purchaseiap_q.push(obj);
        FB.ui(obj, window.onpurchaseiap);
    }

    // register a function for when fb sdk resolves login status
    // see https://developers.facebook.com/docs/facebook-login/web for reference
    FB.getLoginStatus(function (response) {
        // console.log("ON getLoginStatus");
        if (response.status === 'connected') {
            // console.log("ON getLoginStatus connected");
            window.onlogin(response);
        } else {
            // the user isn't logged in to Facebook.
            // console.log("ON getLoginStatus not yet");
            FB.login(function (response) {
                if (response.status === 'connected') {
                    // console.log("ON getLoginStatus manual login OK");
                    // console.log("FB login now connected");
                    window.onlogin(response);
                } else {
                    console.log("ON getLoginStatus manual login FAIL");
                    // console.log("FB login not connected");
                }
            }, {
                scope: 'public_profile,email'
            });
        }
    });
};