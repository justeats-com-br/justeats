import httpretty

from src.restaurants.domain.model.restaurant import Restaurant


class StripeClientMock:
    def mock_add_payment_receive_account_for_restaurant(self, restaurant: Restaurant) -> None:
        httpretty.register_uri(httpretty.POST, "https://api.stripe.com/v1/accounts",
                               body='{"id": "acct_1MXkXJIsAhdg0JnG"}')

    def mock_generate_onboarding_url(self):
        httpretty.register_uri(httpretty.POST, "https://api.stripe.com/v1/account_links",
                               body='''
                               {
                                  "object": "account_link",
                                  "created": 1675615250,
                                  "expires_at": 1675615550,
                                  "url": "https://connect.stripe.com/setup/s/acct_1MXkXJIsAhdg0JnG/HOtNfX600KR9"
                                }
                               ''')

    def mock_load_customer_by_external_id(self, external_id: str, email: str):
        httpretty.register_uri(httpretty.GET, "https://api.stripe.com/v1/customers/%s" % external_id,
                               body='{"id": "%s", "email": "%s"}' % (external_id, email))
