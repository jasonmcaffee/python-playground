import requests
from urllib.parse import urlparse, parse_qs


def main():
    print("running the script...")
    # this is test account info that is not used for anything other than sandbox testing
    client_id = "vpvuomqv25pmesud3n6nfd23a"
    client_secret = "mjsk3ui47igqqri7vj7wbegtre36rciwve6ynda2mcpm5oukke"
    basic_auth = "Basic dnB2dW9tcXYyNXBtZXN1ZDNuNm5mZDIzYTptanNrM3VpNDdpZ3Fxcmk3dmo3d2JlZ3RyZTM2cmNpd3ZlNnluZGEybWNwbTVvdWtrZQ=="
    redirect_uri = "https://recipient.dev.ddp.akoya.com/flow/callback"

    # start the linking process by visiting this url and using mikomo_4 as the user and pass:
    # https://sandbox-idp.ddp.akoya.com/auth?connector=mikomo&client_id=vpvuomqv25pmesud3n6nfd23a&redirect_uri=https%3A%2F%2Frecipient.dev.ddp.akoya.com%2Fflow%2Fcallback&response_type=code&scope=openid%20email%20profile%20offline_access&state=qwe4263gfa3

    # complete the linking process, then paste the full url you are redirected to here
    post_link_url_youre_redirected_to = "REPLACE THIS WITH SOMETHING SIMILAR TO: https://recipient.dev.ddp.akoya.com/flow/callback?code=ory_ac_FlTxdtIHxHCQaiyT7Ev48E5c4zGua1X1fnVmzLFhfhQ.bB047yIjGofK_qh67EIetkhOFoBh8xIUE8OywRarbgg&scope=openid+offline_access&state=qwe4263gfa3"
    code = parse_code_from_url_youre_redirected_to_after_linking(post_link_url_youre_redirected_to)

    # exchange the code for the initial refresh_token
    _, refresh_token = exchange_code_for_tokens(code, basic_auth, redirect_uri)

    # demonstrate the akoya bug
    demonstrate_akoya_refresh_token_bug(client_id, client_secret, refresh_token)

    print("done running script")


# if at any point you use an expired refresh_token when calling refreshToken endpoint, all refresh_token values stop working.
def demonstrate_akoya_refresh_token_bug(client_id, client_secret, original_refresh_token):
    print("refresh token attempt 1...")
    _, refresh_token_1 = refresh_the_tokens(original_refresh_token, client_id, client_secret)
    print(f"attempt 1 new refresh token successfully retrieved: {refresh_token_1}")

    print("refresh token attempt 2...")
    _, refresh_token_2 = refresh_the_tokens(refresh_token_1, client_id, client_secret)
    print(f"attempt 2 new refresh token successfully retrieved: {refresh_token_2}")

    print("refresh token attempt 3...")
    _, refresh_token_3 = refresh_the_tokens(refresh_token_2, client_id, client_secret)
    print(f"attempt 3 new refresh token successfully retrieved: {refresh_token_3}")

    # At this point, refresh_token_3 should be valid
    # Now we will perform an operation that unexpectedly invalidates refresh_token_3, and all other refresh token values,
    # by simply passing in a previous refresh_token that is now expired
    print("### performing operation that will cause all refresh tokens to stop working ###")
    print("refresh token attempt 4 using expired original_refresh_token...")
    try:
        _, _ = refresh_the_tokens(original_refresh_token, client_id, client_secret)
    except Exception as err:
        print(f"An expected error occurred when calling refresh_the_tokens with an expired refresh_token: \n{err}")

    # refresh_token_3 should be valid, as we haven't tried using it.
    print("demonstrate tat refresh_token_3 _unexpectedly_ doesnt work")
    print("refresh token attempt 5...")
    try:
        _, refresh_token_5 = refresh_the_tokens(refresh_token_3, client_id, client_secret)
        print(f"attempt 5 new refresh token successfully retrieved: {refresh_token_5}")
    except Exception as err:
        print(f"unexpectedly can't use refresh_token_3!! \n{err}")


def refresh_the_tokens(refresh_token, client_id, client_secret):
    print(f"refresh_the_token called for refresh_token: {refresh_token}")
    url = "https://sandbox-idp.ddp.akoya.com/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    print(response.text)
    response.raise_for_status()  # raise http error if the status is bad
    json_response = response.json()
    id_token = json_response["id_token"]
    refresh_token = json_response["refresh_token"]
    return id_token, refresh_token


# after you link you are redirected to a 404 page that has the url:
# https://recipient.dev.ddp.akoya.com/flow/callback?code=ory_ac_pSptnP_PrLaWtwSGqqIpXAnIJK21ovreVL9ZmXg5tKU.nPyB1ilk4yE0R91CooOf9uZxpJPD7FGMTNy-fds9tCU&scope=openid+offline_access&state=qwe4263gfa3
def parse_code_from_url_youre_redirected_to_after_linking(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get("code", [None])[0]
    return code


# only done after initial linking through mikomo ui.  The redirect uri will land you on a 404 page, and the url will contain the code.
# e.g. https://recipient.dev.ddp.akoya.com/flow/callback?code=ory_ac_pSptnP_PrLaWtwSGqqIpXAnIJK21ovreVL9ZmXg5tKU.nPyB1ilk4yE0R91CooOf9uZxpJPD7FGMTNy-fds9tCU&scope=openid+offline_access&state=qwe4263gfa3
def exchange_code_for_tokens(code, basic_auth, redirect_uri):
    print("exchanging code for refresh_token")
    url = "https://sandbox-idp.ddp.akoya.com/token"
    payload = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "authorization": basic_auth
    }

    response = requests.post(url, data=payload, headers=headers)
    print(response.text)
    json_response = response.json()
    id_token = json_response["id_token"]
    refresh_token = json_response["refresh_token"]
    return id_token, refresh_token


if __name__ == "__main__":
    main()
